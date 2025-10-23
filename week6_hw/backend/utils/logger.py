"""
统一日志管理
提供结构化的日志记录功能
"""
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from backend.config import settings


class StructuredLogger:
    """结构化日志记录器"""
    
    def __init__(self, name: str = "excel_analysis"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # 确保日志目录存在
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # 创建文件处理器
        file_handler = logging.FileHandler(
            log_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.log",
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def log_file_upload(self, file_name: str, file_size: int, file_id: str):
        """记录文件上传"""
        self.logger.info(json.dumps({
            "event": "file_upload",
            "file_name": file_name,
            "file_size": file_size,
            "file_id": file_id,
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False))
    
    def log_file_processing(self, file_id: str, original_path: str, processed_path: str, 
                           processing_log: Dict[str, Any]):
        """记录文件处理"""
        self.logger.info(json.dumps({
            "event": "file_processing",
            "file_id": file_id,
            "original_path": str(original_path),
            "processed_path": str(processed_path),
            "processing_log": processing_log,
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False))
    
    def log_metadata_generation(self, file_id: str, file_name: str, 
                               summary: str, columns_count: int, embedding_dim: int):
        """记录元数据生成"""
        self.logger.info(json.dumps({
            "event": "metadata_generation",
            "file_id": file_id,
            "file_name": file_name,
            "summary_length": len(summary),
            "columns_count": columns_count,
            "embedding_dim": embedding_dim,
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False))
    
    def log_elasticsearch_index(self, file_id: str, index_name: str, success: bool, error: Optional[str] = None):
        """记录Elasticsearch索引"""
        log_data = {
            "event": "elasticsearch_index",
            "file_id": file_id,
            "index_name": index_name,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        if error:
            log_data["error"] = error
        
        if success:
            self.logger.info(json.dumps(log_data, ensure_ascii=False))
        else:
            self.logger.error(json.dumps(log_data, ensure_ascii=False))
    
    def log_code_generation(self, file_id: str, question: str, code: str, 
                           used_columns: list, analysis_type: str, success: bool, 
                           error: Optional[str] = None, attempt: Optional[int] = None):
        """记录代码生成"""
        log_data = {
            "event": "code_generation",
            "file_id": file_id,
            "question": question,
            "code": code,
            "code_length": len(code),
            "used_columns": used_columns,
            "analysis_type": analysis_type,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        if error:
            log_data["error"] = error
        if attempt:
            log_data["attempt"] = attempt
        
        if success:
            self.logger.info(json.dumps(log_data, ensure_ascii=False))
        else:
            self.logger.error(json.dumps(log_data, ensure_ascii=False))
    
    def log_code_execution(self, file_id: str, code: str, execution_method: str,
                          success: bool, output: Optional[str] = None, 
                          error: Optional[str] = None, execution_time: Optional[float] = None,
                          image_generated: bool = False, attempt: Optional[int] = None):
        """记录代码执行"""
        log_data = {
            "event": "code_execution",
            "file_id": file_id,
            "code": code,
            "execution_method": execution_method,
            "success": success,
            "output_length": len(output) if output else 0,
            "image_generated": image_generated,
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat()
        }
        
        if output:
            log_data["output"] = output
        if error:
            log_data["error"] = error
        if attempt:
            log_data["attempt"] = attempt
        
        if success:
            self.logger.info(json.dumps(log_data, ensure_ascii=False))
        else:
            self.logger.error(json.dumps(log_data, ensure_ascii=False))
    
    def log_file_deletion(self, file_id: str, file_name: str, original_path: str, 
                         processed_path: str, success: bool, error: Optional[str] = None):
        """记录文件删除"""
        log_data = {
            "event": "file_deletion",
            "file_id": file_id,
            "file_name": file_name,
            "original_path": str(original_path),
            "processed_path": str(processed_path),
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        if error:
            log_data["error"] = error
        
        if success:
            self.logger.info(json.dumps(log_data, ensure_ascii=False))
        else:
            self.logger.error(json.dumps(log_data, ensure_ascii=False))
    
    def log_websocket_message(self, client_id: str, message_type: str, content: str, 
                             response_type: str = None, success: bool = True, error: Optional[str] = None):
        """记录WebSocket消息"""
        log_data = {
            "event": "websocket_message",
            "client_id": client_id,
            "message_type": message_type,
            "content_length": len(content),
            "response_type": response_type,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        if error:
            log_data["error"] = error
        
        if success:
            self.logger.info(json.dumps(log_data, ensure_ascii=False))
        else:
            self.logger.error(json.dumps(log_data, ensure_ascii=False))
    
    def log_error(self, event: str, file_id: str = None, error: str = None, **kwargs):
        """记录错误"""
        log_data = {
            "event": event,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        if file_id:
            log_data["file_id"] = file_id
        
        log_data.update(kwargs)
        self.logger.error(json.dumps(log_data, ensure_ascii=False))


# 全局日志记录器实例
logger = StructuredLogger()
