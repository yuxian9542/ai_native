"""
Docker-based安全代码执行服务
在Docker容器中执行Python代码，提供更好的隔离和一致性
"""
import asyncio
import tempfile
import shutil
import base64
import json
import docker
from pathlib import Path
from typing import Dict, Any, Optional
from backend.config import settings
from backend.models.schemas import CodeExecutionResult


class DockerCodeExecutor:
    """Docker代码执行器"""
    
    def __init__(self):
        self.client = docker.from_env()
        self.container_name = "excel-analysis-code-executor"
        self.image_name = "excel-analysis-code-executor"
        
    # 危险代码模式
    FORBIDDEN_PATTERNS = [
        "import os",
        "import subprocess", 
        "import sys",
        "from os import",
        "from subprocess import",
        "from sys import",
        "__import__",
        "eval(",
        "exec(",
        "compile(",
        "open(",  # 会进一步检查是否是写模式
    ]
    
    async def execute_code(
        self,
        code: str,
        csv_file_path: str
    ) -> CodeExecutionResult:
        """
        在Docker容器中执行Python代码
        
        Args:
            code: Python代码
            csv_file_path: CSV数据文件路径
            
        Returns:
            执行结果
        """
        # 1. 安全检查
        if not self._is_code_safe(code):
            return CodeExecutionResult(
                success=False,
                error="代码包含不安全的操作，拒绝执行"
            )
        
        # 2. 准备代码
        full_code = self._prepare_code(code, csv_file_path)
        
        try:
            # 3. 在Docker容器中执行
            result = await self._run_in_docker(full_code)
            return result
            
        except Exception as e:
            return CodeExecutionResult(
                success=False,
                error=f"Docker执行异常: {str(e)}"
            )
    
    def _is_code_safe(self, code: str) -> bool:
        """检查代码是否安全"""
        code_lower = code.lower()
        
        for pattern in self.FORBIDDEN_PATTERNS:
            if pattern.lower() in code_lower:
                # 特殊处理open()，允许读模式
                if pattern == "open(":
                    # 简单检查是否包含写模式
                    if any(mode in code for mode in ["'w'", '"w"', "'a'", '"a"', "'wb'", '"wb"']):
                        return False
                else:
                    return False
        
        return True
    
    def _prepare_code(self, user_code: str, csv_path: str) -> str:
        """准备完整的可执行代码"""
        # 替换路径变量
        user_code = user_code.replace("CSV_FILE_PATH", f"r'{csv_path}'")
        user_code = user_code.replace("OUTPUT_IMAGE_PATH", "r'/app/workspace/output.png'")
        
        # 添加安全头部
        header = """# -*- coding: utf-8 -*-
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial']
plt.rcParams['axes.unicode_minus'] = False

# 设置seaborn样式
sns.set_style("whitegrid")

"""
        
        full_code = header + user_code
        
        return full_code
    
    async def _run_in_docker(self, code: str) -> CodeExecutionResult:
        """在Docker容器中运行代码"""
        try:
            # 确保容器存在
            container = await self._get_or_create_container()
            
            # 将代码写入容器
            exec_result = container.exec_run(
                f"python -c {json.dumps(code)}",
                workdir="/app/workspace",
                timeout=settings.code_execution_timeout
            )
            
            # 获取输出
            output_text = exec_result.output.decode('utf-8', errors='ignore')
            
            # 检查是否有图片生成
            image_base64 = None
            try:
                # 尝试从容器中复制图片
                image_data, _ = container.get_archive("/app/workspace/output.png")
                if image_data:
                    # 读取tar文件并提取图片
                    import tarfile
                    import io
                    
                    tar_stream = io.BytesIO()
                    for chunk in image_data:
                        tar_stream.write(chunk)
                    tar_stream.seek(0)
                    
                    with tarfile.open(fileobj=tar_stream, mode='r') as tar:
                        for member in tar.getmembers():
                            if member.name.endswith('output.png'):
                                image_file = tar.extractfile(member)
                                if image_file:
                                    image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
                                    break
            except:
                pass  # 没有图片生成也没关系
            
            # 判断执行是否成功
            if exec_result.exit_code == 0:
                return CodeExecutionResult(
                    success=True,
                    output=output_text,
                    image=image_base64
                )
            else:
                return CodeExecutionResult(
                    success=False,
                    error=f"代码执行错误 (退出码: {exec_result.exit_code}):\n{output_text}"
                )
                
        except Exception as e:
            return CodeExecutionResult(
                success=False,
                error=f"Docker执行失败: {str(e)}"
            )
    
    async def _get_or_create_container(self):
        """获取或创建Docker容器"""
        try:
            # 尝试获取现有容器
            container = self.client.containers.get(self.container_name)
            if container.status == 'running':
                return container
            else:
                # 启动容器
                container.start()
                return container
        except docker.errors.NotFound:
            # 容器不存在，创建新容器
            return await self._create_container()
    
    async def _create_container(self):
        """创建新的Docker容器"""
        try:
            # 构建镜像（如果不存在）
            try:
                self.client.images.get(self.image_name)
            except docker.errors.ImageNotFound:
                await self._build_image()
            
            # 创建容器
            container = self.client.containers.create(
                image=self.image_name,
                name=self.container_name,
                volumes={
                    str(Path(settings.processed_dir).resolve()): {
                        'bind': '/app/data',
                        'mode': 'ro'
                    },
                    str(Path(__file__).parent.parent.parent.resolve()): {
                        'bind': '/app/backend',
                        'mode': 'ro'
                    }
                },
                working_dir="/app/workspace",
                command="tail -f /dev/null",  # 保持容器运行
                detach=True
            )
            
            # 启动容器
            container.start()
            return container
            
        except Exception as e:
            raise Exception(f"创建Docker容器失败: {str(e)}")
    
    async def _build_image(self):
        """构建Docker镜像"""
        try:
            dockerfile_path = Path(__file__).parent.parent.parent / "docker" / "Dockerfile.code-executor"
            
            # 构建镜像
            image, build_logs = self.client.images.build(
                path=str(dockerfile_path.parent),
                dockerfile="Dockerfile.code-executor",
                tag=self.image_name,
                rm=True
            )
            
            print(f"Docker镜像构建成功: {self.image_name}")
            
        except Exception as e:
            raise Exception(f"构建Docker镜像失败: {str(e)}")
    
    def cleanup(self):
        """清理资源"""
        try:
            container = self.client.containers.get(self.container_name)
            if container.status == 'running':
                container.stop()
            container.remove()
        except:
            pass


# 全局实例
docker_code_executor = DockerCodeExecutor()
