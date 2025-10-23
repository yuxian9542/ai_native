"""
元数据生成服务
生成数据摘要、列描述、语义向量等
"""
import pandas as pd
import uuid
from datetime import datetime
from typing import Dict, Any, List
from backend.utils.openai_client import openai_client
from backend.models.schemas import FileMetadata, ColumnInfo


class MetadataGenerator:
    """元数据生成器"""
    
    async def generate_metadata(
        self,
        file_name: str,
        file_path: str,
        processed_path: str
    ) -> FileMetadata:
        """
        生成完整的文件元数据
        
        Args:
            file_name: 文件名
            file_path: 原始文件路径
            processed_path: 处理后的CSV路径
            
        Returns:
            文件元数据对象
        """
        # 读取处理后的Excel
        df = pd.read_excel(processed_path)
        
        # 确保路径是绝对路径
        from pathlib import Path
        file_path_abs = str(Path(file_path).resolve())
        processed_path_abs = str(Path(processed_path).resolve())
        
        # 生成摘要
        summary = await self._generate_summary(file_name, df)
        
        # 生成列信息
        columns = await self._generate_column_info(df)
        
        # 生成新增字段
        headers = df.columns.tolist()
        first_5_rows = df.head(5).to_dict('records')
        last_5_rows = df.tail(5).to_dict('records')
        column_unique_values = self._extract_unique_values(df)
        
        # 生成embedding向量
        embedding_text = self._prepare_embedding_text(file_name, summary, columns)
        embedding = await openai_client.generate_embedding(embedding_text)
        
        # 构建元数据对象
        metadata = FileMetadata(
            file_id=str(uuid.uuid4()),
            file_name=file_name,
            file_path=file_path_abs,  # 原始文件绝对路径
            processed_path=processed_path_abs,  # 处理后文件绝对路径
            summary=summary,
            columns=columns,
            embedding=embedding,
            headers=headers,
            first_5_rows=first_5_rows,
            last_5_rows=last_5_rows,
            column_unique_values=column_unique_values,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        return metadata
    
    async def _generate_summary(self, file_name: str, df: pd.DataFrame) -> str:
        """
        生成数据摘要
        
        Args:
            file_name: 文件名
            df: DataFrame
            
        Returns:
            50字内的中文摘要
        """
        # 准备上下文
        context = f"""文件名: {file_name}
行数: {len(df)}
列数: {len(df.columns)}
列名: {', '.join(df.columns.tolist()[:10])}
样本数据（前3行）:
{df.head(3).to_string()}
"""
        
        prompt = f"""请为以下Excel数据生成一个50字以内的中文摘要，说明：
1. 数据的主要类型和用途
2. 时间/地域范围（如果能从数据中看出）

{context}

请只返回摘要文字，不要其他内容。"""
        
        messages = [
            {"role": "system", "content": "你是一个数据分析专家，擅长快速理解数据的业务含义。"},
            {"role": "user", "content": prompt}
        ]
        
        try:
            summary = await openai_client.chat_completion(messages, temperature=0.2, max_tokens=200)
            return summary.strip()
        except Exception as e:
            print(f"摘要生成失败: {str(e)}")
            return f"包含{len(df)}行{len(df.columns)}列的数据表"
    
    async def _generate_column_info(self, df: pd.DataFrame) -> List[ColumnInfo]:
        """
        生成列信息
        
        Args:
            df: DataFrame
            
        Returns:
            列信息列表
        """
        columns_info = []
        
        # 批量生成列描述（提高效率）
        columns_data = []
        for col in df.columns:
            col_data = {
                "name": col,
                "type": str(df[col].dtype),
                "non_null_count": int(df[col].count()),
                "unique_count": int(df[col].nunique()),
                "null_count": int(df[col].isna().sum()),
                "sample_values": df[col].dropna().astype(str).head(5).tolist()
            }
            columns_data.append(col_data)
        
        # 批量生成描述
        descriptions = await self._batch_generate_column_descriptions(columns_data)
        
        # 构建ColumnInfo对象
        for col_data, description in zip(columns_data, descriptions):
            col_info = ColumnInfo(
                name=col_data["name"],
                type=col_data["type"],
                description=description,
                sample_values=col_data["sample_values"][:3],
                unique_count=col_data["unique_count"],
                null_count=col_data["null_count"]
            )
            columns_info.append(col_info)
        
        return columns_info
    
    async def _batch_generate_column_descriptions(
        self,
        columns_data: List[Dict[str, Any]]
    ) -> List[str]:
        """
        批量生成列描述
        
        Args:
            columns_data: 列数据列表
            
        Returns:
            描述列表
        """
        # 准备提示词
        columns_text = "\n".join([
            f"{i+1}. 列名: {col['name']}, 类型: {col['type']}, "
            f"唯一值: {col['unique_count']}, 非空: {col['non_null_count']}, "
            f"样本: {col['sample_values'][:3]}"
            for i, col in enumerate(columns_data[:20])  # 限制一次处理20列
        ])
        
        prompt = f"""为以下数据列生成简短描述（每列10字以内），说明业务含义：

{columns_text}

返回JSON格式：
{{
    "descriptions": ["描述1", "描述2", ...]
}}

请只返回JSON，不要其他内容。"""
        
        messages = [
            {"role": "system", "content": "你是一个数据分析专家，擅长理解列的业务含义。"},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await openai_client.chat_completion(messages, temperature=0.1, max_tokens=1000)
            result = openai_client.extract_json(response)
            descriptions = result.get("descriptions", [])
            
            # 如果描述数量不够，用默认值补齐
            while len(descriptions) < len(columns_data):
                descriptions.append("数据列")
            
            return descriptions[:len(columns_data)]
        except Exception as e:
            print(f"批量描述生成失败: {str(e)}")
            return [col["name"] for col in columns_data]
    
    def _prepare_embedding_text(
        self,
        file_name: str,
        summary: str,
        columns: List[ColumnInfo]
    ) -> str:
        """
        准备用于生成embedding的文本
        
        Args:
            file_name: 文件名
            summary: 摘要
            columns: 列信息
            
        Returns:
            组合后的文本
        """
        column_names = ", ".join([col.name for col in columns])
        column_descriptions = ", ".join([col.description for col in columns])
        
        text = f"""文件名: {file_name}
摘要: {summary}
列名: {column_names}
列描述: {column_descriptions}
"""
        return text
    
    def _extract_unique_values(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """
        提取每列的唯一值（最多20个）
        
        Args:
            df: DataFrame
            
        Returns:
            每列唯一值的字典
        """
        column_unique_values = {}
        
        for col in df.columns:
            # 获取唯一值，转换为字符串，去除空值
            unique_vals = df[col].dropna().unique()
            unique_vals_str = [str(val) for val in unique_vals]
            
            # 限制最多20个唯一值
            column_unique_values[col] = unique_vals_str[:20]
        
        return column_unique_values


# 全局实例
metadata_generator = MetadataGenerator()

