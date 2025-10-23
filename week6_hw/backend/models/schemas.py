"""
Pydantic数据模型
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class ColumnInfo(BaseModel):
    """列信息模型"""
    name: str
    type: str
    description: str
    sample_values: List[str]
    unique_count: int
    null_count: int


class FileMetadata(BaseModel):
    """文件元数据模型"""
    file_id: str
    file_name: str
    file_path: str
    processed_path: str
    summary: str
    columns: List[ColumnInfo]
    embedding: Optional[List[float]] = None
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class FileSearchResult(BaseModel):
    """文件检索结果"""
    file_id: str
    file_name: str
    summary: str
    score: float
    columns: List[ColumnInfo]


class CodeGenerationResult(BaseModel):
    """代码生成结果"""
    code: str
    used_columns: List[str]
    analysis_type: str
    expected_output: str


class CodeExecutionResult(BaseModel):
    """代码执行结果"""
    success: bool
    output: Optional[str] = None
    image: Optional[str] = None
    error: Optional[str] = None


class UploadResponse(BaseModel):
    """上传响应"""
    success: bool
    file_id: Optional[str] = None
    file_name: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None


class FileListItem(BaseModel):
    """文件列表项"""
    file_id: str
    file_name: str
    summary: str
    row_count: int
    column_count: int
    created_at: datetime


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    elasticsearch: bool
    openai: str

