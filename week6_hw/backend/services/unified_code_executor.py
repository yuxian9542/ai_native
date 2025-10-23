"""
统一代码执行服务
根据配置选择本地执行或Docker执行
"""
from backend.config import settings
from backend.models.schemas import CodeExecutionResult
from backend.services.code_executor import code_executor
from backend.services.docker_code_executor import docker_code_executor


class UnifiedCodeExecutor:
    """统一代码执行器"""
    
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
        if settings.use_docker_execution:
            try:
                # 尝试使用Docker执行
                return await docker_code_executor.execute_code(code, csv_file_path)
            except Exception as e:
                # Docker执行失败，回退到本地执行
                print(f"Docker执行失败，回退到本地执行: {e}")
                return await code_executor.execute_code(code, csv_file_path)
        else:
            # 使用本地执行
            return await code_executor.execute_code(code, csv_file_path)
    
    def cleanup(self):
        """清理资源"""
        if settings.use_docker_execution:
            try:
                docker_code_executor.cleanup()
            except:
                pass


# 全局实例
unified_code_executor = UnifiedCodeExecutor()
