"""
配置管理模块
从环境变量读取配置
"""
from pydantic_settings import BaseSettings
from pathlib import Path
from dotenv import load_dotenv

# 加载.env文件
load_dotenv(Path(__file__).parent.parent / ".env")


class Settings(BaseSettings):
    """应用配置"""
    
    # OpenAI配置
    openai_api_key: str
    
    # Elasticsearch配置
    elasticsearch_url: str = "http://localhost:9200"
    
    # 服务器配置
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    
    # 数据目录配置
    upload_dir: str = "./data/original"
    processed_dir: str = "./data/processed"
    output_dir: str = "./data/output"
    
    # 执行配置
    code_execution_timeout: int = 60
    max_file_size: int = 52428800  # 50MB
    use_docker_execution: bool = False  # 是否使用Docker执行代码（默认使用虚拟环境）
    
    class Config:
        env_file_encoding = "utf-8"
    
    def ensure_dirs(self):
        """确保数据目录存在"""
        Path(self.upload_dir).mkdir(parents=True, exist_ok=True)
        Path(self.processed_dir).mkdir(parents=True, exist_ok=True)
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)


# 全局配置实例
settings = Settings()
settings.ensure_dirs()

