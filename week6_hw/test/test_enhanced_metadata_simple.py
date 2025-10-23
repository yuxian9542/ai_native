#!/usr/bin/env python3
"""
简单测试增强的元数据功能
"""
import sys
from pathlib import Path
import pandas as pd
import asyncio

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.metadata_generator import metadata_generator


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
    processed_path.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_excel(original_path, index=False)
    df.to_excel(processed_path, index=False)
    print(f"   ✅ Test file created: {original_path}")
    
    # 2. 生成增强元数据
    print("2. Generating enhanced metadata...")
    try:
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
            
        # 显示前5行数据
        print(f"   📊 First 5 rows data:")
        for i, row in enumerate(metadata.first_5_rows):
            print(f"      Row {i+1}: {row}")
            
        print("\n🎉 Enhanced metadata test completed successfully!")
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print("🧪 Testing Enhanced Metadata Generation")
    print("=" * 60)
    
    success = await test_enhanced_metadata()
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Tests failed!")


if __name__ == "__main__":
    asyncio.run(main())
