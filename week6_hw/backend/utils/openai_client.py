"""
OpenAI API客户端封装
"""
import asyncio
import httpx
from openai import AsyncOpenAI
from typing import List, Dict, Any
import json
import re
from backend.config import settings


class OpenAIClient:
    """OpenAI API客户端"""
    
    def __init__(self):
        # Create httpx client without proxies to avoid compatibility issues
        http_client = httpx.AsyncClient()
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            http_client=http_client
        )
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4",
        temperature: float = 0.2,
        max_tokens: int = 2000
    ) -> str:
        """
        调用ChatCompletion API
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            生成的文本
        """
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API调用失败: {str(e)}")
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        生成文本的embedding向量
        
        Args:
            text: 输入文本
            
        Returns:
            1536维向量
        """
        try:
            response = await self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Embedding生成失败: {str(e)}")
    
    def extract_json(self, text: str) -> Dict[str, Any]:
        """
        从文本中提取JSON
        
        Args:
            text: 包含JSON的文本
            
        Returns:
            解析后的JSON对象
        """
        # 清理文本，移除可能的markdown标记
        cleaned_text = text.strip()
        
        # 尝试直接解析
        try:
            return json.loads(cleaned_text)
        except:
            pass
        
        # 尝试提取JSON代码块
        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except:
                pass
        
        # 尝试提取大括号内容
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except:
                pass
        
        # 尝试修复常见的JSON格式问题
        try:
            # 移除可能的额外字符
            start_idx = text.find('{')
            end_idx = text.rfind('}')
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_text = text[start_idx:end_idx + 1]
                
                # 修复控制字符问题
                json_text = self._fix_json_control_chars(json_text)
                
                # 修复未正确引用的字符串值（特别是code字段）
                json_text = self._fix_unquoted_strings(json_text)
                
                return json.loads(json_text)
        except:
            pass
        
        raise ValueError("无法从响应中提取有效的JSON")
    
    def _fix_json_control_chars(self, json_text: str) -> str:
        """修复JSON中的控制字符问题"""
        import re
        
        # 使用正则表达式找到所有字符串值并修复其中的控制字符
        def fix_string(match):
            string_content = match.group(1)
            # 转义控制字符
            string_content = string_content.replace('\n', '\\n')
            string_content = string_content.replace('\r', '\\r')
            string_content = string_content.replace('\t', '\\t')
            string_content = string_content.replace('\b', '\\b')
            string_content = string_content.replace('\f', '\\f')
            string_content = string_content.replace('"', '\\"')
            return f'"{string_content}"'
        
        # 匹配双引号内的字符串
        json_text = re.sub(r'"([^"]*)"', fix_string, json_text)
        
        return json_text
    
    def _fix_unquoted_strings(self, json_text: str) -> str:
        """修复未正确引用的字符串值"""
        import re
        
        # 修复 "code": 后面跟着换行和代码的情况
        # 匹配 "code": \n"""代码内容"""
        code_pattern = r'"code":\s*\n?"""(.*?)"""'
        if re.search(code_pattern, json_text, re.DOTALL):
            def replace_code(match):
                code_content = match.group(1)
                # 转义特殊字符
                escaped_code = code_content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                return f'"code": "{escaped_code}"'
            
            json_text = re.sub(code_pattern, replace_code, json_text, flags=re.DOTALL)
        
        # 修复其他可能的未引用字符串
        # 匹配 "field": 后面跟着未引用的字符串
        unquoted_pattern = r'"(\w+)":\s*\n?"""(.*?)"""'
        if re.search(unquoted_pattern, json_text, re.DOTALL):
            def replace_unquoted(match):
                field_name = match.group(1)
                field_value = match.group(2)
                # 转义特殊字符
                escaped_value = field_value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                return f'"{field_name}": "{escaped_value}"'
            
            json_text = re.sub(unquoted_pattern, replace_unquoted, json_text, flags=re.DOTALL)
        
        return json_text


# 全局实例
openai_client = OpenAIClient()

