"""
Elasticsearch客户端封装
"""
from elasticsearch import AsyncElasticsearch
from typing import List, Dict, Any, Optional
from backend.config import settings
from backend.models.elasticsearch import EXCEL_METADATA_INDEX, EXCEL_METADATA_MAPPING


class ESClient:
    """Elasticsearch客户端"""
    
    def __init__(self):
        self.client = AsyncElasticsearch([settings.elasticsearch_url])
        self.index_name = EXCEL_METADATA_INDEX
    
    async def close(self):
        """关闭连接"""
        await self.client.close()
    
    async def ping(self) -> bool:
        """检查连接"""
        try:
            return await self.client.ping()
        except:
            return False
    
    async def create_index(self):
        """创建索引"""
        try:
            if await self.client.indices.exists(index=self.index_name):
                print(f"索引 {self.index_name} 已存在")
                return
            
            await self.client.indices.create(
                index=self.index_name,
                body=EXCEL_METADATA_MAPPING
            )
            print(f"索引 {self.index_name} 创建成功")
        except Exception as e:
            raise Exception(f"创建索引失败: {str(e)}")
    
    async def index_document(self, doc_id: str, document: Dict[str, Any]):
        """
        索引文档
        
        Args:
            doc_id: 文档ID
            document: 文档内容
        """
        try:
            await self.client.index(
                index=self.index_name,
                id=doc_id,
                document=document
            )
        except Exception as e:
            raise Exception(f"索引文档失败: {str(e)}")
    
    async def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        获取文档
        
        Args:
            doc_id: 文档ID
            
        Returns:
            文档内容
        """
        try:
            result = await self.client.get(index=self.index_name, id=doc_id)
            return result["_source"]
        except:
            return None
    
    async def search(
        self,
        query: Dict[str, Any],
        size: int = 10
    ) -> List[Dict[str, Any]]:
        """
        搜索文档
        
        Args:
            query: 查询条件
            size: 返回数量
            
        Returns:
            搜索结果列表
        """
        try:
            result = await self.client.search(
                index=self.index_name,
                body=query,
                size=size
            )
            return result["hits"]["hits"]
        except Exception as e:
            raise Exception(f"搜索失败: {str(e)}")
    
    async def get_all_documents(self) -> List[Dict[str, Any]]:
        """获取所有文档"""
        try:
            result = await self.client.search(
                index=self.index_name,
                body={"query": {"match_all": {}}},
                size=1000
            )
            return result["hits"]["hits"]
        except:
            return []
    
    async def delete_document(self, doc_id: str) -> bool:
        """
        删除文档
        
        Args:
            doc_id: 文档ID
            
        Returns:
            是否删除成功
        """
        try:
            result = await self.client.delete(
                index=self.index_name,
                id=doc_id
            )
            return result["result"] == "deleted"
        except Exception as e:
            raise Exception(f"删除文档失败: {str(e)}")


# 全局实例
es_client = ESClient()

