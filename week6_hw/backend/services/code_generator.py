"""
Python代码生成服务
根据用户问题和文件元数据生成可执行的分析代码
"""
from typing import Dict, Any
from backend.utils.openai_client import openai_client
from backend.models.schemas import FileSearchResult, CodeGenerationResult
from backend.utils.logger import logger


class CodeGenerator:
    """代码生成器"""
    
    async def generate_code(
        self,
        question: str,
        file_info: FileSearchResult
    ) -> CodeGenerationResult:
        """
        生成分析代码
        
        Args:
            question: 用户问题
            file_info: 选中的文件信息
            
        Returns:
            代码生成结果
        """
        # 构建提示词
        prompt = self._build_prompt(question, file_info)
        
        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": prompt}
        ]
        
        # 调用GPT-4生成代码
        response = await openai_client.chat_completion(
            messages,
            model="gpt-4",
            temperature=0.2,
            max_tokens=2000
        )
        
        # 解析响应
        try:
            result_json = openai_client.extract_json(response)
        except Exception as e:
            logger.log_error(
                "code_generation_json_parse_failed",
                file_info.file_id,
                f"JSON解析失败: {e}",
                raw_response=response[:500]  # 只记录前500字符
            )
            print(f"JSON解析失败: {e}")
            print(f"原始响应: {response}")
            raise
        
        code_result = CodeGenerationResult(
            code=result_json.get("code", ""),
            used_columns=result_json.get("used_columns", []),
            analysis_type=result_json.get("analysis_type", "数据分析"),
            expected_output=result_json.get("expected_output", "")
        )
        
        return code_result

    async def generate_code_with_retry(
        self,
        question: str,
        file_info: FileSearchResult,
        max_retries: int = 3
    ) -> CodeGenerationResult:
        """
        带重试机制的代码生成
        
        Args:
            question: 用户问题
            file_info: 选中的文件信息
            max_retries: 最大重试次数
            
        Returns:
            代码生成结果
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                if attempt == 0:
                    # 第一次尝试，使用原始问题
                    prompt = self._build_prompt(question, file_info)
                else:
                    # 后续尝试，包含错误信息
                    prompt = self._build_prompt_with_error(question, file_info, last_error, attempt)
                
                messages = [
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ]
                
                # 调用GPT-4生成代码
                response = await openai_client.chat_completion(
                    messages,
                    model="gpt-4",
                    temperature=0.2,
                    max_tokens=2000
                )
                
                # 解析响应
                try:
                    result_json = openai_client.extract_json(response)
                    
                    code_result = CodeGenerationResult(
                        code=result_json.get("code", ""),
                        used_columns=result_json.get("used_columns", []),
                        analysis_type=result_json.get("analysis_type", "数据分析"),
                        expected_output=result_json.get("expected_output", "")
                    )
                    
                    # 记录成功生成
                    logger.log_code_generation(
                        file_info.file_id,
                        question,
                        code_result.code,
                        code_result.used_columns,
                        code_result.analysis_type,
                        True,
                        attempt=attempt + 1
                    )
                    
                    return code_result
                    
                except Exception as e:
                    last_error = f"JSON解析失败: {e}"
                    logger.log_error(
                        "code_generation_json_parse_failed",
                        file_info.file_id,
                        f"第{attempt + 1}次尝试JSON解析失败: {e}",
                        raw_response=response[:500]
                    )
                    
            except Exception as e:
                last_error = f"代码生成失败: {e}"
                logger.log_error(
                    "code_generation_failed",
                    file_info.file_id,
                    f"第{attempt + 1}次尝试失败: {e}"
                )
        
        # 所有重试都失败了
        logger.log_error(
            "code_generation_max_retries_exceeded",
            file_info.file_id,
            f"达到最大重试次数{max_retries}，最后错误: {last_error}"
        )
        
        return CodeGenerationResult(
            code="",
            used_columns=[],
            analysis_type="error",
            expected_output=f"代码生成失败，已重试{max_retries}次。最后错误: {last_error}"
        )

    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个专业的Python数据分析师，擅长使用pandas、numpy、matplotlib进行数据分析。

你需要根据用户的问题和数据文件信息，生成可执行的Python代码。

        代码要求：
        1. 使用CSV_FILE_PATH变量作为Excel数据文件路径（注意：这是Excel文件，不是CSV）
        2. 如需生成图表，保存到OUTPUT_IMAGE_PATH
        3. 必须导入pandas、numpy
        4. 如需可视化，导入matplotlib并设置：
           - matplotlib.use('Agg')
           - plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
        5. 处理可能的空值和异常
        6. 使用print()输出清晰的分析结论
        7. 仅使用数据分析库，禁止使用os、subprocess、sys等系统模块
        8. 不能使用input()等交互操作
        9. 数据已经通过df = pd.read_excel(CSV_FILE_PATH)加载，直接使用df变量进行分析
        10. 不要重复加载数据，直接使用已有的df变量

返回JSON格式：
{
    "code": "完整的Python代码",
    "used_columns": ["使用的列名列表"],
    "analysis_type": "分析类型（如：趋势分析、统计汇总等）",
    "expected_output": "预期输出描述"
}"""
    
    def _build_prompt(self, question: str, file_info: FileSearchResult) -> str:
        """构建用户提示词"""
        # 构建列信息文本
        columns_text = "\n".join([
            f"- {col.name} ({col.type}): {col.description}, "
            f"样本值: {col.sample_values}, 唯一值数: {col.unique_count}"
            for col in file_info.columns[:15]  # 限制列数
        ])
        
        prompt = f"""用户问题：{question}

数据文件信息：
- 文件名：{file_info.file_name}
- 摘要：{file_info.summary}
- 列信息：
{columns_text}

请生成Python分析代码，回答用户的问题。
记住：数据文件路径使用变量CSV_FILE_PATH，图片输出路径使用OUTPUT_IMAGE_PATH。
只返回JSON，不要其他解释。"""
        
        return prompt

    def _build_prompt_with_error(
        self,
        question: str,
        file_info: FileSearchResult,
        error_message: str,
        attempt: int
    ) -> str:
        """构建包含错误信息的提示词"""
        # 构建列信息文本
        columns_text = "\n".join([
            f"- {col.name} ({col.type}): {col.description}, "
            f"样本值: {col.sample_values}, 唯一值数: {col.unique_count}"
            for col in file_info.columns[:15]  # 限制列数
        ])

        prompt = f"""用户问题：{question}

数据文件信息：
- 文件名：{file_info.file_name}
- 摘要：{file_info.summary}
- 列信息：
{columns_text}

之前的代码执行失败（第{attempt}次尝试）：
错误信息：{error_message}

请根据错误信息修正代码，确保：
1. 使用正确的列名（检查拼写和大小写）
2. 处理数据类型转换问题
3. 处理空值和异常情况
4. 使用正确的pandas语法
5. 确保所有变量都已定义

请生成修正后的Python分析代码，回答用户的问题。
记住：数据文件路径使用变量CSV_FILE_PATH，图片输出路径使用OUTPUT_IMAGE_PATH。
只返回JSON，不要其他解释。"""
        
        return prompt


# 全局实例
code_generator = CodeGenerator()

