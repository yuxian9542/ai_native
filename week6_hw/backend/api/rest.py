"""
REST API路由
处理文件上传、列表查询等操作
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import shutil
from pathlib import Path
import uuid

from backend.config import settings
from backend.models.schemas import (
    UploadResponse, FileListItem, HealthResponse
)
from backend.services.excel_processor import excel_processor
from backend.services.metadata_generator import metadata_generator
from backend.utils.es_client import es_client
from backend.utils.openai_client import openai_client
from backend.utils.logger import logger


router = APIRouter()


@router.post("/files/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    上传Excel文件
    
    处理流程：
    1. 验证文件类型
    2. 保存到original目录
    3. 预处理Excel
    4. 生成元数据
    5. 索引到ES
    """
    file_id = None
    try:
        # 1. 验证文件类型
        if not file.filename.endswith(('.xlsx', '.xls')):
            logger.log_error("file_upload_validation_failed", error="不支持的文件类型")
            return UploadResponse(
                success=False,
                error="仅支持Excel文件（.xlsx或.xls）"
            )
        
        # 2. 保存原始文件
        file_id = str(uuid.uuid4())
        original_path = Path(settings.upload_dir) / file.filename
        processed_path = Path(settings.processed_dir) / f"{Path(file.filename).stem}_processed.xlsx"
        
        # 记录文件上传
        file.file.seek(0, 2)  # 移动到文件末尾
        file_size = file.file.tell()
        file.file.seek(0)  # 重置到开头
        logger.log_file_upload(file.filename, file_size, file_id)
        
        # 保存上传的文件
        with open(original_path, 'wb') as f:
            shutil.copyfileobj(file.file, f)
        
        # 3. 预处理Excel
        processing_log = await excel_processor.process_excel(
            str(original_path),
            str(processed_path)
        )
        logger.log_file_processing(file_id, original_path, processed_path, processing_log)
        
        # 4. 生成元数据
        metadata = await metadata_generator.generate_metadata(
            file.filename,
            str(original_path),
            str(processed_path)
        )
        logger.log_metadata_generation(
            file_id, 
            file.filename, 
            metadata.summary, 
            len(metadata.columns),
            len(metadata.embedding) if metadata.embedding else 0
        )
        
        # 5. 索引到ES
        doc = metadata.model_dump()
        # 转换datetime为字符串
        doc["created_at"] = doc["created_at"].isoformat()
        doc["updated_at"] = doc["updated_at"].isoformat()
        
        try:
            await es_client.index_document(metadata.file_id, doc)
            logger.log_elasticsearch_index(metadata.file_id, "excel_metadata", True)
        except Exception as e:
            logger.log_elasticsearch_index(metadata.file_id, "excel_metadata", False, str(e))
            raise
        
        return UploadResponse(
            success=True,
            file_id=metadata.file_id,
            file_name=file.filename,
            message="文件上传并处理成功"
        )
        
    except Exception as e:
        return UploadResponse(
            success=False,
            error=f"处理失败: {str(e)}"
        )


@router.get("/files", response_model=dict)
async def list_files():
    """获取所有文件列表"""
    try:
        docs = await es_client.get_all_documents()
        
        files = []
        for doc in docs:
            source = doc["_source"]
            import pandas as pd
            
            # 读取Excel获取行数
            try:
                df = pd.read_excel(source["processed_path"])
                row_count = len(df)
                column_count = len(df.columns)
            except:
                row_count = 0
                column_count = 0
            
            from datetime import datetime
            file_item = FileListItem(
                file_id=source["file_id"],
                file_name=source["file_name"],
                summary=source.get("summary", ""),
                row_count=row_count,
                column_count=column_count,
                created_at=datetime.fromisoformat(source["created_at"])
            )
            files.append(file_item)
        
        return {"files": [f.model_dump() for f in files]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/{file_id}", response_model=dict)
async def get_file_detail(file_id: str):
    """获取文件详情"""
    try:
        doc = await es_client.get_document(file_id)
        if not doc:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        return doc
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    # 检查ES连接
    es_healthy = await es_client.ping()
    
    # 检查OpenAI（简单验证）
    openai_status = "connected" if settings.openai_api_key else "not configured"
    
    return HealthResponse(
        status="healthy" if es_healthy else "unhealthy",
        elasticsearch=es_healthy,
        openai=openai_status
    )


@router.delete("/files/{file_id}")
async def delete_file(file_id: str):
    """
    删除文件
    
    处理流程：
    1. 从ES获取文件信息
    2. 删除处理后的Excel文件（保留原始文件）
    3. 从ES删除文档
    """
    try:
        # 1. 获取文件信息
        doc = await es_client.get_document(file_id)
        if not doc:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        original_path = Path(doc["file_path"])
        processed_path = Path(doc["processed_path"])
        
        # 2. 只删除处理后的Excel文件，保留原始文件
        deleted_files = []
        if processed_path.exists():
            processed_path.unlink()
            deleted_files.append("processed file")
        
        # 3. 从ES删除文档
        await es_client.delete_document(file_id)
        
        # 记录删除操作
        logger.log_file_deletion(
            file_id, 
            doc['file_name'], 
            original_path, 
            processed_path, 
            True
        )
        
        return {
            "success": True,
            "message": f"文件 {doc['file_name']} 的已处理数据已删除（原始文件已保留）"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.log_file_deletion(
            file_id, 
            doc.get('file_name', 'unknown'), 
            original_path, 
            processed_path, 
            False, 
            str(e)
        )
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")

