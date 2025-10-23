#!/usr/bin/env python3
"""
测试Excel处理工作流程
验证Excel文件处理、元数据生成和代码执行
"""
import sys
from pathlib import Path
import pandas as pd
import asyncio

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.excel_processor import ExcelProcessor
from backend.services.metadata_generator import MetadataGenerator
from backend.services.virtualenv_code_executor import virtualenv_code_executor


async def test_excel_workflow():
    """测试完整的Excel处理工作流程"""
    print("🧪 Testing Excel Processing Workflow")
    print("=" * 50)
    
    # 1. 创建测试Excel文件
    print("1. Creating test Excel file...")
    test_data = {
        'product': ['cola', 'sprite', 'fanta', 'cola', 'sprite', 'fanta'],
        'sales': [100, 150, 90, 120, 180, 95],
        'quantity': [10, 15, 9, 12, 18, 10],
        'month': ['Jan', 'Jan', 'Jan', 'Feb', 'Feb', 'Feb']
    }
    
    # 创建原始Excel文件（模拟用户上传）
    original_path = Path("data/original/test_data.xlsx").resolve()
    original_path.parent.mkdir(parents=True, exist_ok=True)
    
    df_original = pd.DataFrame(test_data)
    df_original.to_excel(original_path, index=False)
    print(f"   ✅ Original Excel created: {original_path}")
    
    # 2. 处理Excel文件
    print("2. Processing Excel file...")
    processor = ExcelProcessor()
    processed_path = Path("data/processed/test_data_processed.xlsx").resolve()
    
    try:
        log = await processor.process_excel(str(original_path), str(processed_path))
        print(f"   ✅ Excel processed successfully")
        print(f"   📊 Processing log: {log}")
        
        # 验证处理后的文件
        if processed_path.exists():
            df_processed = pd.read_excel(processed_path)
            print(f"   📈 Processed data shape: {df_processed.shape}")
            print(f"   📋 Processed columns: {list(df_processed.columns)}")
        else:
            print("   ❌ Processed file not found")
            return False
            
    except Exception as e:
        print(f"   ❌ Excel processing failed: {e}")
        return False
    
    # 3. 生成元数据
    print("3. Generating metadata...")
    metadata_gen = MetadataGenerator()
    
    try:
        metadata = await metadata_gen.generate_metadata(
            "test_data.xlsx",
            str(original_path),
            str(processed_path)
        )
        print(f"   ✅ Metadata generated successfully")
        print(f"   📁 File path: {metadata.file_path}")
        print(f"   📊 Summary: {metadata.summary[:100]}...")
        print(f"   📋 Columns: {len(metadata.columns)} columns")
        
        # 验证元数据中的路径
        if metadata.file_path == str(processed_path):
            print("   ✅ Metadata stores processed Excel path correctly")
        else:
            print(f"   ❌ Metadata path mismatch: {metadata.file_path} != {processed_path}")
            return False
            
    except Exception as e:
        print(f"   ❌ Metadata generation failed: {e}")
        return False
    
    # 4. 测试代码执行
    print("4. Testing code execution...")
    test_code = """
# 基本数据分析
print("=== Excel Data Analysis ===")
print(f"Data shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print("\\nFirst 3 rows:")
print(df.head(3))

# 统计摘要
print("\\n=== Statistical Summary ===")
print(df.describe())

# 产品销量分析
print("\\n=== Product Sales Analysis ===")
product_sales = df.groupby('product')['sales'].sum()
print(product_sales)

# 月度销量分析
print("\\n=== Monthly Sales Analysis ===")
monthly_sales = df.groupby('month')['sales'].sum()
print(monthly_sales)
"""
    
    try:
        result = await virtualenv_code_executor.execute_code(test_code, str(processed_path))
        
        if result.success:
            print("   ✅ Code execution successful")
            print(f"   📊 Output length: {len(result.output)} characters")
            print(f"   📈 Sample output: {result.output[:200]}...")
        else:
            print(f"   ❌ Code execution failed: {result.error}")
            return False
            
    except Exception as e:
        print(f"   ❌ Code execution error: {e}")
        return False
    
    print("\\n🎉 Excel workflow test completed successfully!")
    return True


if __name__ == "__main__":
    success = asyncio.run(test_excel_workflow())
    if success:
        print("\\n✅ All tests passed!")
    else:
        print("\\n❌ Some tests failed!")
        sys.exit(1)
