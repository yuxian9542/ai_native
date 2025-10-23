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
        
        # 5. 生成代码
        code_result = await code_generator.generate_code(content, best_file)
        
        # 6. 发送代码
        await manager.send_message(client_id, {
            "type": "code_generated",
            "content": {
                "code": code_result.code,
                "used_columns": code_result.used_columns,
                "analysis_type": code_result.analysis_type
            }
        })
        
        # 7. 发送状态：正在执行
        await manager.send_message(client_id, {
            "type": "status",
            "content": "正在执行分析..."
        })
        
        # 8. 获取CSV文件路径
        file_doc = await es_client.get_document(best_file.file_id)
        csv_path = file_doc["processed_path"]
        
        # 9. 执行代码
        exec_result = await unified_code_executor.execute_code(code_result.code, csv_path)
        
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

