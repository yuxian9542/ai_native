"""
初始化Elasticsearch索引
"""
import asyncio
import sys
from pathlib import Path

# 添加backend到路径
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path.parent))

from backend.utils.es_client import es_client


async def main():
    """初始化ES索引"""
    print("=" * 50)
    print("初始化Elasticsearch索引")
    print("=" * 50)
    
    # 检查连接
    print("1. 检查Elasticsearch连接...")
    connected = await es_client.ping()
    
    if not connected:
        print("✗ 无法连接到Elasticsearch")
        print(f"请确保Elasticsearch运行在: {es_client.client.transport.hosts}")
        await es_client.close()
        return
    
    print("✓ Elasticsearch连接成功")
    
    # 创建索引
    print("\n2. 创建索引...")
    try:
        await es_client.create_index()
        print("✓ 索引创建成功")
    except Exception as e:
        print(f"✗ 索引创建失败: {str(e)}")
    
    await es_client.close()
    print("\n" + "=" * 50)
    print("初始化完成！")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())

