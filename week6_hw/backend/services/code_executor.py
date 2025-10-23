"""
安全代码执行服务
在隔离环境中执行Python代码
"""
import asyncio
import tempfile
import shutil
import base64
from pathlib import Path
from typing import Dict, Any
from backend.config import settings
from backend.models.schemas import CodeExecutionResult


class CodeExecutor:
    """代码执行器"""
    
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
        执行Python代码
        
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
        
        # 2. 创建临时工作目录
        temp_dir = tempfile.mkdtemp(prefix="analysis_")
        
        try:
            # 3. 准备代码
            full_code = self._prepare_code(code, csv_file_path, temp_dir)
            
            # 4. 写入脚本文件
            script_path = Path(temp_dir) / "script.py"
            script_path.write_text(full_code, encoding='utf-8')
            
            # 5. 执行代码
            result = await self._run_script(script_path, temp_dir)
            
            return result
            
        except Exception as e:
            return CodeExecutionResult(
                success=False,
                error=f"执行异常: {str(e)}"
            )
        finally:
            # 6. 清理临时目录
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
    
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
    
    def _prepare_code(self, user_code: str, csv_path: str, temp_dir: str) -> str:
        """准备完整的可执行代码"""
        output_image_path = str(Path(temp_dir) / "output.png")
        
        # 替换路径变量
        user_code = user_code.replace("CSV_FILE_PATH", f"r'{csv_path}'")
        user_code = user_code.replace("OUTPUT_IMAGE_PATH", f"r'{output_image_path}'")
        
        # 添加安全头部
        header = """# -*- coding: utf-8 -*-
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial']
plt.rcParams['axes.unicode_minus'] = False

"""
        
        full_code = header + user_code
        
        return full_code
    
    async def _run_script(
        self,
        script_path: Path,
        work_dir: str
    ) -> CodeExecutionResult:
        """运行Python脚本"""
        try:
            # 创建子进程
            process = await asyncio.create_subprocess_exec(
                "python",
                str(script_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=work_dir
            )
            
            # 等待执行完成（带超时）
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=settings.code_execution_timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                return CodeExecutionResult(
                    success=False,
                    error="代码执行超时（超过60秒）"
                )
            
            # 解码输出
            output_text = stdout.decode('utf-8', errors='ignore')
            error_text = stderr.decode('utf-8', errors='ignore')
            
            # 检查是否有图片生成
            image_path = Path(work_dir) / "output.png"
            image_base64 = None
            
            if image_path.exists():
                with open(image_path, 'rb') as f:
                    image_base64 = base64.b64encode(f.read()).decode('utf-8')
            
            # 判断执行是否成功
            if process.returncode == 0:
                return CodeExecutionResult(
                    success=True,
                    output=output_text,
                    image=image_base64
                )
            else:
                return CodeExecutionResult(
                    success=False,
                    error=f"代码执行错误:\n{error_text}"
                )
                
        except Exception as e:
            return CodeExecutionResult(
                success=False,
                error=f"执行失败: {str(e)}"
            )


# 全局实例
code_executor = CodeExecutor()

