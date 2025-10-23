"""
虚拟环境代码执行服务
在同一个虚拟环境中执行Python代码，避免Docker的复杂性
"""
import asyncio
import tempfile
import shutil
import base64
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from backend.config import settings
from backend.models.schemas import CodeExecutionResult


class VirtualEnvCodeExecutor:
    """虚拟环境代码执行器"""
    
    def __init__(self):
        self.python_executable = sys.executable
        self.work_dir = Path(settings.output_dir).resolve() / "code_execution"
        self.work_dir.mkdir(parents=True, exist_ok=True)
        
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
        excel_file_path: str
    ) -> CodeExecutionResult:
        """
        在虚拟环境中执行Python代码

        Args:
            code: Python代码
            excel_file_path: Excel数据文件路径

        Returns:
            执行结果
        """
        print(f"🔧 VirtualEnv Executor: Starting code execution")
        print(f"📁 Excel file path: {excel_file_path}")
        print(f"📄 Code length: {len(code)}")
        
        # 1. 安全检查
        if not self._is_code_safe(code):
            return CodeExecutionResult(
                success=False,
                error="代码包含不安全的操作，拒绝执行"
            )

        # 2. 创建临时工作目录
        temp_dir = tempfile.mkdtemp(prefix="analysis_", dir=self.work_dir)
        print(f"📂 Temp directory: {temp_dir}")

        try:
            # 3. 准备代码
            full_code = self._prepare_code(code, excel_file_path, temp_dir)
            print(f"📝 Prepared code length: {len(full_code)}")

            # 4. 写入脚本文件
            script_path = Path(temp_dir) / "script.py"
            script_path.write_text(full_code, encoding='utf-8')
            print(f"💾 Script saved to: {script_path}")

            # 5. 执行代码
            result = await self._run_script(script_path, temp_dir)
            print(f"✅ Execution completed: {result.success}")
            if not result.success:
                print(f"❌ Error: {result.error}")

            return result

        except Exception as e:
            import traceback
            error_msg = f"执行异常: {str(e)}\n\n堆栈跟踪:\n{traceback.format_exc()}"
            print(f"💥 Exception in execute_code: {error_msg}")
            return CodeExecutionResult(
                success=False,
                error=error_msg
            )
        finally:
            # 6. 清理临时目录
            try:
                shutil.rmtree(temp_dir)
                print(f"🗑️ Cleaned up temp directory: {temp_dir}")
            except Exception as cleanup_e:
                print(f"⚠️ Failed to cleanup temp directory: {cleanup_e}")
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
    
    def _prepare_code(self, user_code: str, excel_path: str, temp_dir: str) -> str:
        """准备完整的可执行代码"""
        output_image_path = str(Path(temp_dir) / "output.png")
        
        # 替换路径变量
        user_code = user_code.replace("CSV_FILE_PATH", f"r'{excel_path}'")
        user_code = user_code.replace("OUTPUT_IMAGE_PATH", f"r'{output_image_path}'")
        
        # 添加安全头部
        header = f"""# -*- coding: utf-8 -*-
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

# 尝试导入seaborn（可选）
try:
    import seaborn as sns
    sns.set_style("whitegrid")
except ImportError:
    pass

# 读取Excel文件
df = pd.read_excel(r'{excel_path}')

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
            print(f"🚀 Starting subprocess execution")
            print(f"🐍 Python executable: {self.python_executable}")
            print(f"📄 Script path: {script_path}")
            print(f"📂 Working directory: {work_dir}")
            
            # 创建子进程，使用相同的Python解释器
            # Windows需要特殊处理
            import platform
            if platform.system() == "Windows":
                # Windows使用subprocess.run而不是asyncio.create_subprocess_exec
                import subprocess
                print(f"🪟 Using Windows subprocess.run")
                
                # 使用更详细的错误处理配置
                try:
                    result = subprocess.run(
                        [self.python_executable, str(script_path)],
                        cwd=work_dir,
                        env=self._get_safe_env(),
                        capture_output=True,
                        text=True,
                        timeout=settings.code_execution_timeout,
                        encoding='utf-8',
                        errors='strict'  # 使用strict模式保留所有错误信息
                    )
                except UnicodeDecodeError as e:
                    print(f"⚠️ UTF-8 strict decode failed: {e}, trying with replace mode")
                    # 如果strict模式失败，回退到replace模式
                    result = subprocess.run(
                        [self.python_executable, str(script_path)],
                        cwd=work_dir,
                        env=self._get_safe_env(),
                        capture_output=True,
                        text=True,
                        timeout=settings.code_execution_timeout,
                        encoding='utf-8',
                        errors='replace'
                    )
                
                print(f"✅ Windows subprocess completed with return code: {result.returncode}")
                print(f"📤 stdout length: {len(result.stdout)}")
                print(f"📤 stderr length: {len(result.stderr)}")
                
                # 详细输出内容（用于调试和日志）
                stdout_content = result.stdout.strip() if result.stdout else ""
                stderr_content = result.stderr.strip() if result.stderr else ""
                
                print(f"📤 STDOUT:\n{stdout_content}")
                print(f"📤 STDERR:\n{stderr_content}")
                
                # 记录到日志
                from backend.utils.logger import logger
                logger.logger.info(f"Code execution stdout: {stdout_content}")
                if stderr_content:
                    logger.logger.error(f"Code execution stderr: {stderr_content}")
                
                # 检查是否有图片生成
                image_path = Path(work_dir) / "output.png"
                image_base64 = None
                
                if image_path.exists():
                    with open(image_path, 'rb') as f:
                        image_base64 = base64.b64encode(f.read()).decode('utf-8')
                
                # 判断执行是否成功
                if result.returncode == 0:
                    return CodeExecutionResult(
                        success=True,
                        output=result.stdout,
                        image=image_base64
                    )
                else:
                    # 组合stdout和stderr信息，保留所有详细信息
                    combined_error = f"进程退出码: {result.returncode}\n"
                    combined_error += f"Python解释器: {self.python_executable}\n"
                    combined_error += f"工作目录: {work_dir}\n"
                    combined_error += f"脚本路径: {script_path}\n\n"
                    
                    if stdout_content:
                        combined_error += f"标准输出:\n{stdout_content}\n\n"
                    else:
                        combined_error += "标准输出: (空)\n\n"
                    
                    if stderr_content:
                        combined_error += f"错误输出:\n{stderr_content}\n\n"
                    else:
                        combined_error += "错误输出: (空)\n\n"
                    
                    # 添加原始字节信息（如果编码有问题）
                    if hasattr(result, 'stdout_bytes') and result.stdout_bytes:
                        combined_error += f"原始stdout字节长度: {len(result.stdout_bytes)}\n"
                    if hasattr(result, 'stderr_bytes') and result.stderr_bytes:
                        combined_error += f"原始stderr字节长度: {len(result.stderr_bytes)}\n"
                    
                    return CodeExecutionResult(
                        success=False,
                        error=f"代码执行错误:\n{combined_error}"
                    )
            else:
                # 非Windows系统使用asyncio
                process = await asyncio.create_subprocess_exec(
                    self.python_executable,
                    str(script_path),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=work_dir,
                    env=self._get_safe_env()
                )
                print(f"🔄 Process created with PID: {process.pid}")
                
                # 等待执行完成（带超时）
                try:
                    print(f"⏳ Waiting for process completion (timeout: {settings.code_execution_timeout}s)")
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(),
                        timeout=settings.code_execution_timeout
                    )
                    print(f"✅ Process completed with return code: {process.returncode}")
                except asyncio.TimeoutError:
                    print(f"⏰ Process timed out, killing...")
                    process.kill()
                    return CodeExecutionResult(
                        success=False,
                        error="代码执行超时（超过60秒）"
                    )
                
                # 解码输出，处理编码问题，保留详细信息
                try:
                    output_text = stdout.decode('utf-8', errors='strict')
                    print(f"📤 Decoded stdout length: {len(output_text)}")
                except UnicodeDecodeError as e:
                    print(f"⚠️ UTF-8 strict decode failed: {e}, trying replace mode")
                    output_text = stdout.decode('utf-8', errors='replace')
                    print(f"📤 Decoded stdout length (replace): {len(output_text)}")
                except Exception as e:
                    print(f"⚠️ UTF-8 decode failed: {e}, trying cp1252")
                    output_text = stdout.decode('cp1252', errors='replace')
                    print(f"📤 Decoded stdout length (cp1252): {len(output_text)}")
                
                try:
                    error_text = stderr.decode('utf-8', errors='strict')
                    print(f"📤 Decoded stderr length: {len(error_text)}")
                except UnicodeDecodeError as e:
                    print(f"⚠️ UTF-8 strict decode failed: {e}, trying replace mode")
                    error_text = stderr.decode('utf-8', errors='replace')
                    print(f"📤 Decoded stderr length (replace): {len(error_text)}")
                except Exception as e:
                    print(f"⚠️ UTF-8 decode failed: {e}, trying cp1252")
                    error_text = stderr.decode('cp1252', errors='replace')
                    print(f"📤 Decoded stderr length (cp1252): {len(error_text)}")
                
                # 详细输出内容（用于调试和日志）
                stdout_content = output_text.strip() if output_text else ""
                stderr_content = error_text.strip() if error_text else ""
                
                print(f"📤 STDOUT:\n{stdout_content}")
                print(f"📤 STDERR:\n{stderr_content}")
                
                # 记录到日志
                from backend.utils.logger import logger
                logger.logger.info(f"Code execution stdout: {stdout_content}")
                if stderr_content:
                    logger.logger.error(f"Code execution stderr: {stderr_content}")
                
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
                    # 组合stdout和stderr信息，保留所有详细信息
                    combined_error = f"进程退出码: {process.returncode}\n"
                    combined_error += f"Python解释器: {self.python_executable}\n"
                    combined_error += f"工作目录: {work_dir}\n"
                    combined_error += f"脚本路径: {script_path}\n"
                    combined_error += f"进程PID: {process.pid}\n\n"
                    
                    if stdout_content:
                        combined_error += f"标准输出:\n{stdout_content}\n\n"
                    else:
                        combined_error += "标准输出: (空)\n\n"
                    
                    if stderr_content:
                        combined_error += f"错误输出:\n{stderr_content}\n\n"
                    else:
                        combined_error += "错误输出: (空)\n\n"
                    
                    # 添加原始字节信息
                    combined_error += f"原始stdout字节长度: {len(stdout)}\n"
                    combined_error += f"原始stderr字节长度: {len(stderr)}\n"
                    
                    return CodeExecutionResult(
                        success=False,
                        error=f"代码执行错误:\n{combined_error}"
                    )
                
        except Exception as e:
            import traceback
            error_details = f"执行异常: {str(e)}\n\n堆栈跟踪:\n{traceback.format_exc()}"
            return CodeExecutionResult(
                success=False,
                error=error_details
            )
    
    def _get_safe_env(self) -> Dict[str, str]:
        """获取安全的环境变量"""
        import os
        
        # 获取当前环境变量
        env = os.environ.copy()
        
        # 移除危险的环境变量
        dangerous_vars = [
            'PATH', 'PYTHONPATH', 'LD_LIBRARY_PATH', 'DYLD_LIBRARY_PATH',
            'HOME', 'USER', 'USERNAME', 'SHELL', 'TERM'
        ]
        
        for var in dangerous_vars:
            env.pop(var, None)
        
        # 设置安全的环境变量
        env.update({
            'PYTHONPATH': str(Path(__file__).parent.parent.parent),
            'PYTHONUNBUFFERED': '1',
            'MPLBACKEND': 'Agg',
            'PYTHONIOENCODING': 'utf-8',
            'LANG': 'en_US.UTF-8',
            'LC_ALL': 'en_US.UTF-8'
        })
        
        return env
    
    def test_environment(self) -> bool:
        """测试执行环境"""
        test_code = """
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

print("Environment test successful!")
print(f"pandas version: {pd.__version__}")
print(f"numpy version: {np.__version__}")

# Create test data
data = {"x": [1, 2, 3], "y": [2, 4, 6]}
df = pd.DataFrame(data)
print(f"DataFrame shape: {df.shape}")

# Create test chart
plt.figure(figsize=(6, 4))
plt.plot(df["x"], df["y"], "o-")
plt.title("Environment Test Chart")
plt.savefig("test_output.png")
print("Chart generation successful!")
"""
        
        try:
            # 创建临时测试文件
            test_file = self.work_dir / "test_env.py"
            test_file.write_text(test_code, encoding='utf-8')
            
            # 执行测试
            result = subprocess.run(
                [self.python_executable, str(test_file)],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.work_dir),
                env=self._get_safe_env()
            )
            
            # 清理测试文件
            test_file.unlink(missing_ok=True)
            
            if result.returncode == 0:
                print(f"环境测试输出: {result.stdout}")
                return True
            else:
                print(f"环境测试失败: {result.stderr}")
                return False
            
        except Exception as e:
            print(f"环境测试异常: {e}")
            return False


# 全局实例
virtualenv_code_executor = VirtualEnvCodeExecutor()
