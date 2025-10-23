#!/usr/bin/env python3
"""
测试增强的元数据和重试功能
"""
import sys
from pathlib import Path
import pandas as pd
import asyncio

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.metadata_generator import metadata_generator
from backend.services.code_generator import code_generator
from backend.services.virtualenv_code_executor import virtualenv_code_executor
from backend.utils.es_client import es_client
from backend.utils.logger import logger


async def test_enhanced_metadata():
    """测试增强的元数据生成"""
    print("📊 Testing Enhanced Metadata Generation")
    print("=" * 50)
    
    # 1. 创建测试文件
    print("1. Creating test file...")
    test_data = {
        'product': ['cola', 'sprite', 'fanta', 'pepsi', 'mountain_dew'],
        'sales': [100, 150, 90, 120, 80],
        'quantity': [10, 15, 9, 12, 8],
        'category': ['beverage', 'beverage', 'beverage', 'beverage', 'beverage'],
        'region': ['north', 'south', 'east', 'west', 'central']
    }
    
    df = pd.DataFrame(test_data)
    original_path = Path('data/original/test_enhanced_metadata.xlsx').resolve()
    processed_path = Path('data/processed/test_enhanced_metadata_processed.xlsx').resolve()
    original_path.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_excel(original_path, index=False)
    print(f"   ✅ Test file created: {original_path}")
    
    # 2. 处理文件并生成增强元数据
    print("2. Processing file and generating enhanced metadata...")
    from backend.services.excel_processor import excel_processor
    await excel_processor.process_excel(str(original_path), str(processed_path))
    
    metadata = await metadata_generator.generate_metadata(
        'test_enhanced_metadata.xlsx',
        str(original_path),
        str(processed_path)
    )
    
    print(f"   ✅ Metadata generated with ID: {metadata.file_id}")
    print(f"   📁 Original path: {metadata.file_path}")
    print(f"   📁 Processed path: {metadata.processed_path}")
    print(f"   📋 Headers: {metadata.headers}")
    print(f"   📊 First 5 rows: {len(metadata.first_5_rows)} rows")
    print(f"   📊 Last 5 rows: {len(metadata.last_5_rows)} rows")
    print(f"   🔢 Column unique values: {len(metadata.column_unique_values)} columns")
    
    # 显示每列的唯一值
    for col, values in metadata.column_unique_values.items():
        print(f"      - {col}: {values}")
    
    # 3. 存储到Elasticsearch
    print("3. Storing metadata to Elasticsearch...")
    doc = metadata.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await es_client.index_document(metadata.file_id, doc)
    print(f"   ✅ Metadata stored with ID: {metadata.file_id}")
    
    return metadata


async def test_retry_logic():
    """测试重试逻辑"""
    print("\n🔄 Testing Retry Logic")
    print("=" * 50)
    
    # 创建文件搜索结果对象
    from backend.models.schemas import FileSearchResult, ColumnInfo
    file_search_result = FileSearchResult(
        file_id="test-retry-file-id",
        file_name="test_retry.xlsx",
        summary="测试重试功能的数据文件",
        score=1.0,
        columns=[
            ColumnInfo(
                name="product",
                type="object",
                description="产品名称",
                sample_values=["cola", "sprite", "fanta"],
                unique_count=5,
                null_count=0
            ),
            ColumnInfo(
                name="sales",
                type="int64",
                description="销售额",
                sample_values=["100", "150", "90"],
                unique_count=5,
                null_count=0
            )
        ]
    )
    
    # 测试带重试的代码生成
    print("1. Testing code generation with retry...")
    try:
        code_result = await code_generator.generate_code_with_retry(
            "分析产品销量数据",
            file_search_result,
            max_retries=3
        )
        print(f"   ✅ Code generation result: {code_result.success}")
        print(f"   📄 Generated code length: {len(code_result.code)}")
        print(f"   📋 Used columns: {code_result.used_columns}")
        print(f"   🔍 Analysis type: {code_result.analysis_type}")
    except Exception as e:
        print(f"   ❌ Code generation failed: {e}")


async def test_error_feedback():
    """测试错误反馈功能"""
    print("\n🔄 Testing Error Feedback")
    print("=" * 50)
    
    # 创建测试文件
    test_data = {
        'product': ['cola', 'sprite', 'fanta'],
        'sales': [100, 150, 90],
        'quantity': [10, 15, 9]
    }
    
    df = pd.DataFrame(test_data)
    test_file = Path('data/processed/test_error_feedback.xlsx').resolve()
    test_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(test_file, index=False)
    
    # 测试有错误的代码
    print("1. Testing code with intentional error...")
    error_code = """
# 故意制造错误 - 使用不存在的列名
result = df['nonexistent_column'].sum()
print(f"结果: {result}")
"""
    
    try:
        result = await virtualenv_code_executor.execute_code(error_code, str(test_file))
        print(f"   📊 Execution result: {result.success}")
        if not result.success:
            print(f"   ❌ Error captured: {result.error[:200]}...")
            
            # 模拟重试逻辑
            print("2. Simulating retry with error feedback...")
            from backend.models.schemas import FileSearchResult, ColumnInfo
            file_info = FileSearchResult(
                file_id="test-error-feedback",
                file_name="test_error_feedback.xlsx",
                summary="测试错误反馈的数据文件",
                score=1.0,
                columns=[
                    ColumnInfo(
                        name="product",
                        type="object",
                        description="产品名称",
                        sample_values=["cola", "sprite", "fanta"],
                        unique_count=3,
                        null_count=0
                    ),
                    ColumnInfo(
                        name="sales",
                        type="int64",
                        description="销售额",
                        sample_values=["100", "150", "90"],
                        unique_count=3,
                        null_count=0
                    )
                ]
            )
            
            # 使用错误信息重新生成代码
            retry_result = await code_generator.generate_code_with_retry(
                "分析产品销量数据",
                file_info,
                max_retries=1
            )
            print(f"   🔄 Retry result: {retry_result.success}")
            print(f"   📄 Retry code length: {len(retry_result.code)}")
            
    except Exception as e:
        print(f"   💥 Exception: {e}")


async def main():
    """主测试函数"""
    print("🧪 Testing Enhanced Metadata and Retry Functionality")
    print("=" * 60)
    
    try:
        # 测试增强元数据
        metadata = await test_enhanced_metadata()
        
        # 测试重试逻辑
        await test_retry_logic()
        
        # 测试错误反馈
        await test_error_feedback()
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
