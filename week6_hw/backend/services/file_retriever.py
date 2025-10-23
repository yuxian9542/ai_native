"""
文件检索服务
使用混合检索（BM25 + 向量相似度）查找最相关的Excel文件
"""
from typing import List
from backend.utils.es_client import es_client
from backend.utils.openai_client import openai_client
from backend.models.schemas import FileSearchResult, ColumnInfo


class FileRetriever:
    """文件检索器"""
    
    async def search_files(self, question: str, top_k: int = 3) -> List[FileSearchResult]:
        """
        检索相关文件
        
        Args:
            question: 用户问题
            top_k: 返回top-k个结果
            
        Returns:
            检索结果列表
        """
        # 1. 生成问题的embedding向量
        question_embedding = await openai_client.generate_embedding(question)
        
        # 2. 构建混合检索查询
        query = self._build_hybrid_query(question, question_embedding)
        
        # 3. 执行搜索
        results = await es_client.search(query, size=top_k)
        
        # 4. 转换为FileSearchResult
        search_results = []
        for hit in results:
            source = hit["_source"]
            
            # 转换列信息
            columns = [
                ColumnInfo(**col) for col in source.get("columns", [])
            ]
            
            result = FileSearchResult(
                file_id=source["file_id"],
                file_name=source["file_name"],
                summary=source.get("summary", ""),
                score=hit["_score"],
                columns=columns
            )
            search_results.append(result)
        
        return search_results
    
    def _build_hybrid_query(self, question: str, embedding: List[float]) -> dict:
        """
        构建混合检索查询
        
        Args:
            question: 用户问题
            embedding: 问题的向量表示
            
        Returns:
            ES查询字典
        """
        query = {
            "query": {
                "script_score": {
                    "query": {
                        "bool": {
                            "should": [
                                # 关键词检索（BM25）
                                {
                                    "multi_match": {
                                        "query": question,
                                        "fields": [
                                            "file_name^3",
                                            "summary^2",
                                            "columns.name^2",
                                            "columns.description^1"
                                        ],
                                        "type": "best_fields",
                                        "fuzziness": "AUTO"
                                    }
                                }
                            ]
                        }
                    },
                    "script": {
                        "source": """
                            double vectorScore = cosineSimilarity(params.query_vector, 'embedding') + 1.0;
                            double bm25Score = _score;
                            return vectorScore * 10 + bm25Score * 0.3;
                        """,
                        "params": {
                            "query_vector": embedding
                        }
                    }
                }
            }
        }
        
        return query


# 全局实例
file_retriever = FileRetriever()

