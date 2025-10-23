"""
统一代码执行服务
根据配置选择虚拟环境执行或本地执行
"""
from backend.config import settings
from backend.models.schemas import CodeExecutionResult
from backend.services.code_executor import code_executor
from backend.services.virtualenv_code_executor import virtualenv_code_executor


class UnifiedCodeExecutor:
    """统一代码执行器"""
    
    def __init__(self):
        self.execution_method = self._determine_execution_method()
    
    def _determine_execution_method(self) -> str:
        """确定执行方法"""
        # 优先使用虚拟环境执行
        return "virtualenv"
    
    async def execute_code(
        self,
        code: str,
        excel_file_path: str
    ) -> CodeExecutionResult:
        """
        执行Python代码（使用虚拟环境）
        
        Args:
            code: Python代码
            excel_file_path: Excel数据文件路径
            
        Returns:
            执行结果
        """
        try:
            # 使用虚拟环境执行
            result = await virtualenv_code_executor.execute_code(code, excel_file_path)
            return result
        except Exception as e:
            import traceback
            # 虚拟环境执行失败，回退到本地执行
            print(f"虚拟环境执行失败，回退到本地执行: {e}")
            print(f"堆栈跟踪: {traceback.format_exc()}")
            
            try:
                # 尝试本地执行
                result = await code_executor.execute_code(code, excel_file_path)
                return result
            except Exception as local_e:
                import traceback
                # 本地执行也失败
                error_details = f"虚拟环境执行失败: {str(e)}\n\n本地执行也失败: {str(local_e)}\n\n虚拟环境堆栈跟踪:\n{traceback.format_exc()}"
                from backend.models.schemas import CodeExecutionResult
                return CodeExecutionResult(
                    success=False,
                    error=error_details
                )
    
    def test_environment(self) -> bool:
        """测试执行环境"""
        return virtualenv_code_executor.test_environment()
    
    def cleanup(self):
        """清理资源"""
        # 虚拟环境执行不需要特殊清理
        pass


# 全局实例
unified_code_executor = UnifiedCodeExecutor()
