"""
Python代码生成服务
根据用户问题和文件元数据生成可执行的分析代码
"""
import ast
import traceback
from typing import Dict, Any, Tuple, Optional
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
        # 第一步：数据分析和解释
        print("🔍 开始数据分析...")
        data_analysis = await self._analyze_data_requirements(question, file_info)
        print(f"📊 数据分析结果: {data_analysis}")
        
        # 第二步：构建包含数据分析的提示词
        prompt = self._build_prompt_with_analysis(question, file_info, data_analysis)
        
        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": prompt}
        ]
        
        # 调用GPT-5生成代码
        response = await openai_client.chat_completion(
            messages,
            model="gpt-4.1",
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
        
        # 获取生成的代码
        generated_code = result_json.get("code", "")
        
        # 第三步：语法检查和修复
        print("🔧 开始语法检查和修复...")
        fixed_code, fix_success, fix_error = await self.check_and_fix_syntax_errors(generated_code)
        
        if fix_success and fixed_code != generated_code:
            print("✅ 代码已自动修复语法错误")
            logger.log_info(
                "code_syntax_fixed",
                file_info.file_id,
                "代码语法错误已自动修复",
                original_code_length=len(generated_code),
                fixed_code_length=len(fixed_code)
            )
        elif not fix_success:
            print(f"⚠️ 语法修复失败: {fix_error}")
            logger.log_error(
                "code_syntax_fix_failed",
                file_info.file_id,
                f"语法修复失败: {fix_error}"
            )
        
        code_result = CodeGenerationResult(
            code=fixed_code,  # 使用修复后的代码
            used_columns=result_json.get("used_columns", []),
            analysis_type=result_json.get("analysis_type", "数据分析"),
            expected_output=result_json.get("expected_output", ""),
            data_analysis=data_analysis  # 添加数据分析结果
        )
        
        return code_result

    async def _analyze_data_requirements(self, question: str, file_info: FileSearchResult) -> Dict[str, Any]:
        """
        分析用户问题需要什么数据和函数
        
        Args:
            question: 用户问题
            file_info: 文件信息
            
        Returns:
            数据分析结果
        """
        try:
            # 构建数据分析提示词
            analysis_prompt = f"""
请分析以下用户问题需要什么数据和函数：

用户问题: {question}

文件信息:
- 文件名: {file_info.file_name}
- 工作表: {file_info.sheet_name}
- 列信息: {[col.name for col in file_info.columns] if file_info.columns else []}
- 列详细信息: {[f"{col.name} ({col.type}): {col.description}" for col in file_info.columns[:10]] if file_info.columns else []}
- 数据样本: {file_info.metadata.get('sample_data', []) if file_info.metadata else []}

请分析并返回JSON格式结果：
{{
    "required_data": {{
        "tables": ["需要哪些表"],
        "columns": ["需要哪些列"],
        "data_types": ["数据类型分析"]
    }},
    "required_functions": ["sum", "avg", "count", "max", "min", "groupby", "filter", "sort"],
    "data_values": {{
        "column_name": ["具体数值列表"],
        "column_name2": ["具体数值列表"]
    }},
    "analysis_explanation": "详细解释需要什么数据，为什么需要这些数据，如何使用这些数据"
}}

注意：
1. 根据用户问题确定需要哪些列的数据
2. 确定需要什么统计函数（sum、avg、count等）
3. 显示具体的数据数值
4. 解释为什么需要这些数据
"""
            
            # 调用GPT-4进行数据分析
            response = await openai_client.chat_completion(
                [{"role": "user", "content": analysis_prompt}],
                model="gpt-4",
                temperature=0.1,
                max_tokens=1500
            )
            
            # 解析JSON响应
            result = openai_client.extract_json(response)
            
            print(f"📊 数据分析完成:")
            print(f"  - 需要的数据: {result.get('required_data', {})}")
            print(f"  - 需要的函数: {result.get('required_functions', [])}")
            print(f"  - 数据解释: {result.get('analysis_explanation', '')}")
            
            return result
            
        except Exception as e:
            print(f"❌ 数据分析失败: {e}")
            # 返回默认分析结果
            return {
                "required_data": {
                    "tables": [file_info.sheet_name or "未知表"],
                    "columns": [col.name for col in file_info.columns] if file_info.columns else [],
                    "data_types": [col.type for col in file_info.columns] if file_info.columns else ["未知类型"]
                },
                "required_functions": ["sum", "avg"],
                "data_values": {},
                "analysis_explanation": f"基于用户问题'{question}'，需要分析文件'{file_info.file_name}'的数据"
            }

    def _build_prompt_with_analysis(self, question: str, file_info: FileSearchResult, data_analysis: Dict[str, Any]) -> str:
        """
        构建包含数据分析的提示词
        
        Args:
            question: 用户问题
            file_info: 文件信息
            data_analysis: 数据分析结果
            
        Returns:
            完整的提示词
        """
        # 获取基础文件信息
        file_path = file_info.processed_file_path or "未知文件路径"
        sheet_name = file_info.sheet_name or "Sheet1"
        
        # 构建数据分析部分
        analysis_section = f"""
## 数据分析结果
根据用户问题分析，需要以下数据和函数：

### 需要的数据:
- 表格: {', '.join(data_analysis.get('required_data', {}).get('tables', []))}
- 列: {', '.join(data_analysis.get('required_data', {}).get('columns', []))}
- 数据类型: {', '.join(data_analysis.get('required_data', {}).get('data_types', []))}

### 需要的函数:
{', '.join(data_analysis.get('required_functions', []))}

### 具体数据数值:
"""
        
        # 添加具体数据数值
        data_values = data_analysis.get('data_values', {})
        for column, values in data_values.items():
            if values:
                analysis_section += f"- {column}: {values[:10]}{'...' if len(values) > 10 else ''}\n"
        
        analysis_section += f"""
### 分析解释:
{data_analysis.get('analysis_explanation', '')}

## 代码生成要求
基于以上数据分析，生成Python代码来回答用户问题。
"""
        
        # 构建完整的提示词
        prompt = f"""
用户问题: {question}

文件信息:
- 文件路径: {file_path}
- 工作表: {sheet_name}
- 列信息: {file_info.metadata.get('columns', []) if file_info.metadata else []}

{analysis_section}

请生成Python代码来分析数据并回答用户问题。代码应该：
1. 读取指定的Excel文件和工作表
2. 使用分析中确定的数据列和函数
3. 生成清晰的结果和可视化图表
4. 包含详细的注释说明

返回JSON格式：
{{
    "code": "生成的Python代码",
    "used_columns": ["使用的列名列表"],
    "analysis_type": "分析类型",
    "expected_output": "预期输出描述"
}}
"""
        
        return prompt

    async def generate_code_with_retry(
        self,
        question: str,
        file_info: FileSearchResult,
        max_retries: int = 3,
        error_message: str = None
    ) -> CodeGenerationResult:
        """
        带重试机制的代码生成
        
        Args:
            question: 用户问题
            file_info: 选中的文件信息
            max_retries: 最大重试次数
            error_message: 执行错误信息（用于重新生成代码）
            
        Returns:
            代码生成结果
        """
        last_error = error_message
        
        for attempt in range(max_retries):
            try:
                if attempt == 0 and not error_message:
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

标准库导入:

Pandas: 必须使用 import pandas as pd。同时，为了完整显示数据，应设置 pd.set_option('display.max_columns', None) 和 pd.set_option('display.max_rows', None)。
目的：确保在打印 DataFrame 时，所有行和列都能完整显示，避免因输出内容被截断而丢失关键信息。
Warnings: 必须使用 import warnings 并通过 warnings.simplefilter(action='ignore', category=Warning) 屏蔽不必要的警告信息。
目的：保持控制台输出的整洁性，让用户能专注于代码执行的核心结果，而不是被次要的警告信息干扰。
编码风格:

命名规范: 变量和函数命名应避免使用中文或特殊符号（如 #），以防范语法错误。
目的：保证代码的兼容性和可移植性，避免因编码问题或特殊字符与语法冲突而导致的潜在错误。
保持列名: 在处理数据时，必须保持原始列名中的特殊字符（如下划线、多空格）不变。
目的：维持数据的原始结构和上下文，确保后续操作或用户在核对数据时，列名与源文件完全一致。
稳健性:

异常处理: 生成的代码必须包含 try...except 等异常处理机制，确保程序的稳定性。
目的：防止程序因意外错误（如文件格式问题、数据类型不匹配）而中断执行，提高代码的容错能力。
数值转换: 在进行数值计算（如求和、排序）前，使用 pd.to_numeric(series, errors='coerce') 将数据列转换为数值类型，并忽略任何无法转换的错误。
目的：确保所有计算操作都在正确的数值类型上进行。errors='coerce' 会将无法转换的值设为 NaN（非数字），从而避免程序因个别脏数据而报错，保证了数据处理流程的顺畅。
弃用方法: 注意 DataFrame.fillna() 方法的 method 参数已不推荐使用，应采用其他方式填充。
目的：遵循库的最佳实践，确保代码在未来版本的 Pandas 中依然能够正常运行，提高代码的长期可维护性。

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
        # 构建详细的列信息文本
        columns_text = "\n".join([
            f"- {col.name} ({col.type}): {col.description}\n"
            f"  样本值: {col.sample_values}, 唯一值数: {col.unique_count}, 空值数: {col.null_count}"
            for col in file_info.columns[:15]  # 限制列数
        ])
        
        # 添加数据类型统计
        data_types = {}
        for col in file_info.columns:
            dtype = col.type
            if dtype not in data_types:
                data_types[dtype] = []
            data_types[dtype].append(col.name)
        
        data_types_text = "\n".join([
            f"- {dtype}: {', '.join(cols)}"
            for dtype, cols in data_types.items()
        ])
        
        prompt = f"""用户问题：{question}

数据文件信息：
- 文件名：{file_info.file_name}
- 工作表：{file_info.sheet_name or '默认工作表'}
- 摘要：{file_info.summary}

列详细信息：
{columns_text}

数据类型分布：
{data_types_text}

请根据以上列信息生成Python分析代码，回答用户的问题。
注意：
1. 使用准确的列名和数据类型
2. 考虑空值处理（null_count > 0的列）
3. 利用列描述理解数据的业务含义
4. 数据文件路径使用变量CSV_FILE_PATH，图片输出路径使用OUTPUT_IMAGE_PATH
5. 只返回JSON，不要其他解释。"""
        
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
    
    async def check_and_fix_syntax_errors(self, code: str) -> Tuple[str, bool, Optional[str]]:
        """
        检查并修复代码语法错误
        
        Args:
            code: 要检查的Python代码
            
        Returns:
            (修复后的代码, 是否修复成功, 错误信息)
        """
        print("🔍 开始语法错误检查...")
        
        # 第一步：使用AST检查语法
        syntax_error = self._check_syntax_with_ast(code)
        if not syntax_error:
            print("✅ 语法检查通过")
            return code, True, None
        
        print(f"❌ 发现语法错误: {syntax_error}")
        
        # 第二步：使用GPT-4修复语法错误
        try:
            fixed_code = await self._fix_syntax_with_gpt4(code, syntax_error)
            if fixed_code:
                # 验证修复后的代码
                verification_error = self._check_syntax_with_ast(fixed_code)
                if not verification_error:
                    print("✅ 语法错误修复成功")
                    return fixed_code, True, None
                else:
                    print(f"❌ 修复后仍有语法错误: {verification_error}")
                    return code, False, f"修复失败: {verification_error}"
            else:
                print("❌ GPT-4修复失败")
                return code, False, "GPT-4修复失败"
        except Exception as e:
            print(f"❌ 修复过程异常: {e}")
            return code, False, f"修复异常: {str(e)}"
    
    def _check_syntax_with_ast(self, code: str) -> Optional[str]:
        """
        使用AST检查Python代码语法
        
        Args:
            code: 要检查的代码
            
        Returns:
            语法错误信息，如果没有错误返回None
        """
        try:
            ast.parse(code)
            return None
        except SyntaxError as e:
            error_msg = f"语法错误: {e.msg}\n位置: 第{e.lineno}行, 第{e.offset}列"
            if e.text:
                error_msg += f"\n问题代码: {e.text.strip()}"
            return error_msg
        except Exception as e:
            return f"解析错误: {str(e)}"
    
    async def _fix_syntax_with_gpt4(self, code: str, syntax_error: str) -> Optional[str]:
        """
        使用GPT-4修复语法错误
        
        Args:
            code: 有语法错误的代码
            syntax_error: 语法错误信息
            
        Returns:
            修复后的代码，如果修复失败返回None
        """
        prompt = f"""请修复以下Python代码的语法错误。

原始代码:
```python
{code}
```

语法错误信息:
{syntax_error}

修复要求:
1. 保持代码的原始功能和逻辑
2. 只修复语法错误，不要改变代码结构
3. 确保修复后的代码可以正常执行
4. 保持注释和变量名不变

请只返回修复后的完整Python代码，不要其他解释。"""

        messages = [
            {
                "role": "system", 
                "content": "你是一个专业的Python代码修复专家，擅长快速识别和修复语法错误。"
            },
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await openai_client.chat_completion(
                messages,
                model="gpt-4",
                temperature=0.1,
                max_tokens=2000
            )
            
            # 提取代码
            fixed_code = self._extract_code_from_response(response)
            return fixed_code
            
        except Exception as e:
            print(f"GPT-4修复调用失败: {e}")
            return None
    
    def _extract_code_from_response(self, response: str) -> Optional[str]:
        """
        从GPT-4响应中提取Python代码
        
        Args:
            response: GPT-4的响应文本
            
        Returns:
            提取的Python代码，如果提取失败返回None
        """
        try:
            # 尝试提取代码块
            if "```python" in response:
                start = response.find("```python") + 9
                end = response.find("```", start)
                if end != -1:
                    code = response[start:end].strip()
                    return code
            
            # 尝试提取代码块（没有语言标识）
            if "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                if end != -1:
                    code = response[start:end].strip()
                    # 简单检查是否像Python代码
                    if any(keyword in code for keyword in ['import', 'def', 'print', 'pd.', 'df.', 'plt.']):
                        return code
            
            # 如果没有代码块标记，尝试直接使用响应
            if any(keyword in response for keyword in ['import', 'def', 'print', 'pd.', 'df.', 'plt.']):
                return response.strip()
            
            return None
            
        except Exception as e:
            print(f"代码提取失败: {e}")
            return None


# 全局实例
code_generator = CodeGenerator()

