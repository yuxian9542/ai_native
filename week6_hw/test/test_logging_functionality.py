#!/usr/bin/env python3
"""
测试日志功能
验证代码生成和执行日志记录
"""
import sys
from pathlib import Path
import pandas as pd
import asyncio
import requests
import json

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.excel_processor import ExcelProcessor
from backend.services.metadata_generator import MetadataGenerator
from backend.services.code_generator import CodeGenerator
from backend.services.virtualenv_code_executor import virtualenv_code_executor
from backend.utils.es_client import es_client
from backend.utils.logger import logger


async def test_logging_functionality():
    """测试日志功能"""
    print("📝 Testing Logging Functionality")
    print("=" * 50)
    
    # 1. 创建测试文件
    print("1. Creating test file...")
    test_data = {
        'product': ['cola', 'sprite', 'fanta'],
        'sales': [100, 150, 90],
        'quantity': [10, 15, 9],
        'month': ['Jan', 'Jan', 'Jan']
    }
    
    df = pd.DataFrame(test_data)
    original_path = Path('data/original/test_logging.xlsx').resolve()
    processed_path = Path('data/processed/test_logging_processed.xlsx').resolve()
    original_path.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_excel(original_path, index=False)
    print(f"   ✅ Test file created: {original_path}")
    
    # 2. 处理文件并生成元数据
    print("2. Processing file and generating metadata...")
    processor = ExcelProcessor()
    await processor.process_excel(str(original_path), str(processed_path))
    
    metadata_gen = MetadataGenerator()
    metadata = await metadata_gen.generate_metadata(
        'test_logging.xlsx',
        str(original_path),
        str(processed_path)
    )
    
    doc = metadata.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await es_client.index_document(metadata.file_id, doc)
    print(f"   ✅ Metadata stored with ID: {metadata.file_id}")
    
    # 3. 测试代码生成日志
    print("3. Testing code generation logging...")
    code_gen = CodeGenerator()
    
    # 创建文件搜索结果对象
    from backend.models.schemas import FileSearchResult, ColumnInfo
    file_search_result = FileSearchResult(
        file_id=metadata.file_id,
        file_name=metadata.file_name,
        summary=metadata.summary,
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
    
    try:
        code_result = await code_gen.generate_code("分析产品销量", file_search_result)
        print(f"   ✅ Code generation successful")
        print(f"   📊 Generated code length: {len(code_result.code)}")
        print(f"   📋 Used columns: {code_result.used_columns}")
        print(f"   🔍 Analysis type: {code_result.analysis_type}")
    except Exception as e:
        print(f"   ❌ Code generation failed: {e}")
        return False
    
    # 4. 测试代码执行日志
    print("4. Testing code execution logging...")
    test_code = """
# 基本数据分析
print("=== 产品销量分析 ===")
print(f"数据形状: {df.shape}")
print(f"列名: {list(df.columns)}")

# 产品销量统计
product_sales = df.groupby('product')['sales'].sum()
print("\\n产品销量:")
print(product_sales)

# 创建简单图表
import matplotlib.pyplot as plt
plt.figure(figsize=(8, 6))
product_sales.plot(kind='bar')
plt.title('产品销量对比')
plt.xlabel('产品')
plt.ylabel('销量')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(OUTPUT_IMAGE_PATH)
print("\\n图表已保存")
"""
    
    try:
        exec_result = await virtualenv_code_executor.execute_code(test_code, str(processed_path))
        print(f"   ✅ Code execution successful: {exec_result.success}")
        if exec_result.success:
            print(f"   📊 Output length: {len(exec_result.output)}")
            print(f"   🖼️  Image generated: {exec_result.image is not None}")
        else:
            print(f"   ❌ Execution error: {exec_result.error}")
    except Exception as e:
        print(f"   ❌ Code execution failed: {e}")
        return False
    
    # 5. 检查日志文件
    print("5. Checking log files...")
    log_file = Path("logs/excel_analysis_20251023.log")
    if log_file.exists():
        with open(log_file, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        # 检查是否包含代码生成日志
        if '"event": "code_generation"' in log_content:
            print("   ✅ Code generation logs found")
        else:
            print("   ❌ Code generation logs not found")
        
        # 检查是否包含代码执行日志
        if '"event": "code_execution"' in log_content:
            print("   ✅ Code execution logs found")
        else:
            print("   ❌ Code execution logs not found")
        
        # 显示最新的几行日志
        log_lines = log_content.strip().split('\n')
        print(f"   📄 Total log entries: {len(log_lines)}")
        print("   📋 Latest log entries:")
        for line in log_lines[-3:]:
            try:
                log_data = json.loads(line.split(' - ', 3)[-1])
                print(f"      - {log_data.get('event', 'unknown')}: {log_data.get('success', 'N/A')}")
            except:
                print(f"      - {line}")
    else:
        print("   ❌ Log file not found")
        return False
    
    print("\\n🎉 Logging functionality test completed!")
    return True


if __name__ == "__main__":
    success = asyncio.run(test_logging_functionality())
    if success:
        print("\\n✅ All logging tests passed!")
    else:
        print("\\n❌ Some logging tests failed!")
        sys.exit(1)
