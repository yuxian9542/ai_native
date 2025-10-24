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
    
    def __init__(self):
        # 简单的内存缓存
        self._embedding_cache = {}
        self._search_cache = {}
    
    async def search_files(self, question: str, top_k: int = 3) -> List[FileSearchResult]:
        """
        检索相关文件
        
        Args:
            question: 用户问题
            top_k: 返回top-k个结果
            
        Returns:
            检索结果列表
        """
        import time
        start_time = time.time()
        
        # 1. 生成问题的embedding向量（带缓存和超时）
        try:
            import asyncio
            import hashlib
            
            # 检查缓存
            question_hash = hashlib.md5(question.encode()).hexdigest()
            if question_hash in self._embedding_cache:
                question_embedding = self._embedding_cache[question_hash]
                print(f"📊 使用缓存的Embedding")
            else:
                question_embedding = await asyncio.wait_for(
                    openai_client.generate_embedding(question),
                    timeout=5.0  # 5秒超时
                )
                # 缓存结果
                self._embedding_cache[question_hash] = question_embedding
                print(f"📊 生成新Embedding并缓存")
            
            embedding_time = time.time() - start_time
            print(f"📊 Embedding处理时间: {embedding_time:.4f}秒")
        except asyncio.TimeoutError:
            print("⚠️ Embedding生成超时，使用简化检索")
            # 使用简化检索作为备选
            return await self._fallback_search(question, top_k)
        
        # 2. 构建混合检索查询
        query = self._build_hybrid_query(question, question_embedding)
        
        # 3. 执行搜索（带超时）
        try:
            results = await asyncio.wait_for(
                es_client.search(query, size=top_k),
                timeout=3.0  # 3秒超时
            )
            search_time = time.time() - start_time - embedding_time
            print(f"📊 ES搜索时间: {search_time:.4f}秒")
        except asyncio.TimeoutError:
            print("⚠️ ES搜索超时，使用简化检索")
            return await self._fallback_search(question, top_k)
        
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
    
    async def _fallback_search(self, question: str, top_k: int) -> List[FileSearchResult]:
        """
        备选检索方法（当主要检索超时时使用）
        
        Args:
            question: 用户问题
            top_k: 返回top-k个结果
            
        Returns:
            检索结果列表
        """
        try:
            # 使用简单的关键词搜索
            simple_query = {
                "query": {
                    "multi_match": {
                        "query": question,
                        "fields": ["file_name^2", "summary", "columns.name", "columns.description"],
                        "type": "best_fields",
                        "fuzziness": "AUTO"
                    }
                },
                "size": top_k
            }
            
            results = await es_client.search(simple_query, size=top_k)
            
            # 转换为FileSearchResult
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
            
            print(f"📊 使用备选检索，找到 {len(search_results)} 个结果")
            return search_results
            
        except Exception as e:
            print(f"❌ 备选检索失败: {e}")
            return []
    
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

