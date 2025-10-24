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
    file_path: str  # 原始文件绝对路径
    processed_path: str  # 处理后文件绝对路径
    summary: str
    columns: List[ColumnInfo]
    embedding: Optional[List[float]] = None
    tags: List[str] = Field(default_factory=list)
    # 新增字段用于代码生成
    headers: List[str] = Field(default_factory=list)  # 列名列表
    first_5_rows: List[Dict[str, Any]] = Field(default_factory=list)  # 前5行数据
    last_5_rows: List[Dict[str, Any]] = Field(default_factory=list)  # 后5行数据
    column_unique_values: Dict[str, List[str]] = Field(default_factory=dict)  # 每列最多20个唯一值
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class FileSearchResult(BaseModel):
    """文件检索结果"""
    file_id: str
    file_name: str
    summary: str
    score: float
    columns: List[ColumnInfo]
    processed_file_path: Optional[str] = None  # 处理后文件路径
    sheet_name: Optional[str] = None  # 工作表名称
    metadata: Optional[Dict[str, Any]] = None  # 元数据


class CodeGenerationResult(BaseModel):
    """代码生成结果"""
    code: str
    used_columns: List[str]
    analysis_type: str
    expected_output: str
    data_analysis: Optional[Dict[str, Any]] = None  # 数据分析结果


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

