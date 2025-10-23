"""
WebSocket处理
实时双向通信，处理用户问题并流式返回结果
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict
import json
import uuid

from backend.services.file_retriever import file_retriever
from backend.services.code_generator import code_generator
from backend.services.unified_code_executor import unified_code_executor
from backend.utils.es_client import es_client
from backend.utils.logger import logger


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket) -> str:
        """接受连接"""
        await websocket.accept()
        client_id = str(uuid.uuid4())
        self.active_connections[client_id] = websocket
        return client_id
    
    def disconnect(self, client_id: str):
        """断开连接"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
    
    async def send_message(self, client_id: str, message: dict):
        """发送消息"""
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(
                json.dumps(message, ensure_ascii=False)
            )


manager = ConnectionManager()


async def handle_websocket(websocket: WebSocket):
    """处理WebSocket连接"""
    client_id = await manager.connect(websocket)
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 处理消息
            await process_message(client_id, message)
            
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        print(f"WebSocket错误: {str(e)}")
        await manager.send_message(client_id, {
            "type": "error",
            "content": f"处理错误: {str(e)}"
        })
        manager.disconnect(client_id)


async def process_message(client_id: str, message: dict):
    """
    处理用户消息
    
    完整流程：
    1. 检索相关文件
    2. 生成分析代码
    3. 执行代码
    4. 返回结果
    """
    try:
        msg_type = message.get("type", "text")
        content = message.get("content", "")
        
        if not content:
            await manager.send_message(client_id, {
                "type": "error",
                "content": "消息内容为空"
            })
            return
        
        # 1. 发送状态：正在检索
        await manager.send_message(client_id, {
            "type": "status",
            "content": "正在检索相关文件..."
        })
        
        # 2. 检索文件
        search_results = await file_retriever.search_files(content, top_k=3)
        
        if not search_results:
            await manager.send_message(client_id, {
                "type": "error",
                "content": "未找到相关数据文件，请先上传Excel文件"
            })
            return
        
        # 3. 发送检索结果
        await manager.send_message(client_id, {
            "type": "files_found",
            "content": {
                "files": [
                    {
                        "name": f.file_name,
                        "summary": f.summary,
                        "score": round(f.score, 2)
                    }
                    for f in search_results
                ]
            }
        })
        
        # 使用得分最高的文件
        best_file = search_results[0]
        
        # 4. 发送状态：正在生成代码
        await manager.send_message(client_id, {
            "type": "status",
            "content": "正在生成分析代码..."
        })
        
        # 5. 获取Excel文件路径
        file_doc = await es_client.get_document(best_file.file_id)
        excel_path = file_doc["processed_path"]
        
        # 6. 带重试的代码生成和执行
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # 生成代码（第一次使用原始问题，后续包含错误信息）
                if attempt == 0:
                    code_result = await code_generator.generate_code(content, best_file)
                else:
                    code_result = await code_generator.generate_code_with_retry(
                        content, best_file, max_retries=1
                    )
                
                # 记录代码生成
                logger.log_code_generation(
                    best_file.file_id,
                    content,
                    code_result.code,
                    code_result.used_columns,
                    code_result.analysis_type,
                    True,
                    attempt=attempt + 1
                )
                
                # 发送代码
                await manager.send_message(client_id, {
                    "type": "code_generated",
                    "content": {
                        "code": code_result.code,
                        "used_columns": code_result.used_columns,
                        "analysis_type": code_result.analysis_type,
                        "attempt": attempt + 1,
                        "max_attempts": max_retries
                    }
                })
                
                # 发送状态：正在执行
                await manager.send_message(client_id, {
                    "type": "status",
                    "content": f"正在执行分析... (第{attempt + 1}/{max_retries}次尝试)"
                })
                
                # 发送详细执行信息
                await manager.send_message(client_id, {
                    "type": "execution_info",
                    "content": {
                        "attempt": attempt + 1,
                        "max_attempts": max_retries,
                        "code_length": len(code_result.code),
                        "used_columns": code_result.used_columns,
                        "analysis_type": code_result.analysis_type
                    }
                })
                
                # 记录执行开始
                logger.log_websocket_message(
                    client_id,
                    "code_execution_start",
                    f"Executing code for file {best_file.file_name} (attempt {attempt + 1})",
                    "status"
                )
                
                # 执行代码
                import time
                start_time = time.time()
                try:
                    exec_result = await unified_code_executor.execute_code(code_result.code, excel_path)
                    execution_time = time.time() - start_time
                    
                    # 记录执行结果
                    logger.log_code_execution(
                        best_file.file_id,
                        code_result.code,
                        "virtualenv",
                        exec_result.success,
                        exec_result.output,
                        exec_result.error,
                        execution_time,
                        exec_result.image is not None,
                        attempt=attempt + 1
                    )
                    
                    if exec_result.success:
                        # 执行成功，跳出重试循环
                        break
                    else:
                        # 执行失败，记录错误并准备重试
                        last_error = exec_result.error
                        logger.log_error(
                            "code_execution_failed_retry",
                            best_file.file_id,
                            f"第{attempt + 1}次执行失败: {last_error}",
                            attempt=attempt + 1
                        )
                        
                        # 发送详细错误信息
                        await manager.send_message(client_id, {
                            "type": "execution_error",
                            "content": {
                                "attempt": attempt + 1,
                                "max_attempts": max_retries,
                                "error": last_error,
                                "execution_time": execution_time,
                                "code_length": len(code_result.code)
                            }
                        })
                        
                        if attempt < max_retries - 1:
                            # 还有重试机会，发送重试消息
                            await manager.send_message(client_id, {
                                "type": "status",
                                "content": f"执行失败，正在重试... (第{attempt + 2}/{max_retries}次尝试)"
                            })
                            
                            # 发送重试原因
                            await manager.send_message(client_id, {
                                "type": "retry_reason",
                                "content": {
                                    "reason": "代码执行失败",
                                    "error_summary": last_error[:200] + "..." if len(last_error) > 200 else last_error,
                                    "next_attempt": attempt + 2
                                }
                            })
                        else:
                            # 最后一次尝试也失败了
                            await manager.send_message(client_id, {
                                "type": "error",
                                "content": f"代码执行失败，已重试{max_retries}次。最后错误: {last_error}"
                            })
                            return
                            
                except Exception as e:
                    execution_time = time.time() - start_time
                    last_error = str(e)
                    
                    # 记录执行异常
                    logger.log_code_execution(
                        best_file.file_id,
                        code_result.code,
                        "virtualenv",
                        False,
                        None,
                        last_error,
                        execution_time,
                        False,
                        attempt=attempt + 1
                    )
                    
                    # 发送详细异常信息
                    await manager.send_message(client_id, {
                        "type": "execution_exception",
                        "content": {
                            "attempt": attempt + 1,
                            "max_attempts": max_retries,
                            "exception": last_error,
                            "execution_time": execution_time,
                            "code_length": len(code_result.code) if 'code_result' in locals() else 0
                        }
                    })
                    
                    if attempt < max_retries - 1:
                        # 还有重试机会
                        await manager.send_message(client_id, {
                            "type": "status",
                            "content": f"执行异常，正在重试... (第{attempt + 2}/{max_retries}次尝试)"
                        })
                        
                        # 发送重试原因
                        await manager.send_message(client_id, {
                            "type": "retry_reason",
                            "content": {
                                "reason": "代码执行异常",
                                "error_summary": last_error[:200] + "..." if len(last_error) > 200 else last_error,
                                "next_attempt": attempt + 2
                            }
                        })
                    else:
                        # 最后一次尝试也失败了
                        await manager.send_message(client_id, {
                            "type": "error",
                            "content": f"代码执行异常，已重试{max_retries}次。最后异常: {last_error}"
                        })
                        return
                        
            except Exception as e:
                # 代码生成失败
                last_error = f"代码生成失败: {str(e)}"
                logger.log_error(
                    "code_generation_failed_retry",
                    best_file.file_id,
                    f"第{attempt + 1}次代码生成失败: {last_error}",
                    attempt=attempt + 1
                )
                
                # 发送代码生成失败信息
                await manager.send_message(client_id, {
                    "type": "code_generation_error",
                    "content": {
                        "attempt": attempt + 1,
                        "max_attempts": max_retries,
                        "error": last_error,
                        "file_id": best_file.file_id
                    }
                })
                
                if attempt < max_retries - 1:
                    await manager.send_message(client_id, {
                        "type": "status",
                        "content": f"代码生成失败，正在重试... (第{attempt + 2}/{max_retries}次尝试)"
                    })
                    
                    # 发送重试原因
                    await manager.send_message(client_id, {
                        "type": "retry_reason",
                        "content": {
                            "reason": "代码生成失败",
                            "error_summary": last_error[:200] + "..." if len(last_error) > 200 else last_error,
                            "next_attempt": attempt + 2
                        }
                    })
                else:
                    await manager.send_message(client_id, {
                        "type": "error",
                        "content": f"代码生成失败，已重试{max_retries}次。最后错误: {last_error}"
                    })
                    return
        
        # 10. 发送最终结果
        if exec_result.success:
            await manager.send_message(client_id, {
                "type": "analysis_complete",
                "content": {
                    "success": True,
                    "output": exec_result.output,
                    "image": exec_result.image,
                    "used_file": best_file.file_name,
                    "used_columns": code_result.used_columns,
                    "code": code_result.code,
                    "file_summary": best_file.summary
                }
            })
        else:
            await manager.send_message(client_id, {
                "type": "error",
                "content": exec_result.error
            })
        
    except Exception as e:
        await manager.send_message(client_id, {
            "type": "error",
            "content": f"处理失败: {str(e)}"
        })

