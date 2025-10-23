#!/usr/bin/env python3
"""
简单的英文代码执行测试
"""
import sys
import asyncio
import pandas as pd
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.services.virtualenv_code_executor import virtualenv_code_executor


async def test_simple_english():
    """测试简单的英文代码执行"""
    print("🐍 Simple English Code Execution Test")
    print("=" * 50)
    
    # 1. 创建测试数据
    print("1. Creating test data...")
    test_csv_path = PROJECT_ROOT / "data" / "processed" / "test_english.csv"
    
    test_data = {
        "product": ["cola", "sprite", "cola", "sprite", "fanta"],
        "sales": [100, 150, 120, 180, 90],
        "quantity": [10, 15, 12, 18, 9],
        "month": ["Jan", "Jan", "Feb", "Feb", "Jan"]
    }
    
    df = pd.DataFrame(test_data)
    df.to_csv(test_csv_path, index=False, encoding='utf-8')
    print(f"   ✅ Test data created: {len(df)} rows")
    
    # 2. 测试简单代码
    print("\n2. Testing simple code execution...")
    simple_code = """
# Read data
df = pd.read_csv(CSV_FILE_PATH)
print("Data shape:", df.shape)
print("Columns:", list(df.columns))
print("First 3 rows:")
print(df.head(3))
"""
    
    try:
        result = await virtualenv_code_executor.execute_code(simple_code, str(test_csv_path))
        
        if result.success:
            print("   ✅ Simple code execution successful")
            print("   Output:")
            print(result.output)
        else:
            print(f"   ❌ Simple code execution failed: {result.error}")
            
    except Exception as e:
        print(f"   ❌ Simple code execution exception: {e}")
    
    # 3. 测试数据分析
    print("\n3. Testing data analysis...")
    analysis_code = """
# Read data
df = pd.read_csv(CSV_FILE_PATH)

# Basic statistics
print("=== Basic Statistics ===")
print(df.describe())

# Group by product
print("\\n=== Product Statistics ===")
product_stats = df.groupby('product')['sales'].sum()
print(product_stats)

# Monthly statistics
print("\\n=== Monthly Statistics ===")
monthly_stats = df.groupby('month')['sales'].sum()
print(monthly_stats)
"""
    
    try:
        result = await virtualenv_code_executor.execute_code(analysis_code, str(test_csv_path))
        
        if result.success:
            print("   ✅ Data analysis successful")
            print("   Output:")
            print(result.output)
        else:
            print(f"   ❌ Data analysis failed: {result.error}")
            
    except Exception as e:
        print(f"   ❌ Data analysis exception: {e}")
    
    # 4. 测试图表生成
    print("\n4. Testing chart generation...")
    chart_code = """
# Read data
df = pd.read_csv(CSV_FILE_PATH)

# Create chart
plt.figure(figsize=(10, 6))
sales_by_product = df.groupby('product')['sales'].sum()
plt.bar(sales_by_product.index, sales_by_product.values, color='skyblue')
plt.title('Sales by Product')
plt.xlabel('Product')
plt.ylabel('Sales')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(OUTPUT_IMAGE_PATH, dpi=300, bbox_inches='tight')

print("Chart generated successfully!")
print(f"Sales by product: {sales_by_product.to_dict()}")
"""
    
    try:
        result = await virtualenv_code_executor.execute_code(chart_code, str(test_csv_path))
        
        if result.success:
            print("   ✅ Chart generation successful")
            print("   Output:")
            print(result.output)
            
            if result.image:
                print("   ✅ Chart image generated")
                # Save image
                output_dir = PROJECT_ROOT / "data" / "output"
                output_dir.mkdir(exist_ok=True)
                
                import base64
                image_data = base64.b64decode(result.image)
                image_path = output_dir / "test_english_chart.png"
                with open(image_path, 'wb') as f:
                    f.write(image_data)
                print(f"   📊 Chart saved: {image_path}")
            else:
                print("   ⚠️  No chart image generated")
        else:
            print(f"   ❌ Chart generation failed: {result.error}")
            
    except Exception as e:
        print(f"   ❌ Chart generation exception: {e}")
    
    print("\n🎉 Simple English test completed!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(test_simple_english())

