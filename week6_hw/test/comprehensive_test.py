#!/usr/bin/env python3
"""
综合代码执行测试
测试虚拟环境代码执行的各种功能
"""
import sys
import asyncio
import pandas as pd
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.services.virtualenv_code_executor import virtualenv_code_executor


async def test_comprehensive():
    """综合测试"""
    print("🐍 Comprehensive Code Execution Test")
    print("=" * 60)
    
    # 1. 环境测试
    print("1. Testing execution environment...")
    if virtualenv_code_executor.test_environment():
        print("   ✅ Environment test passed")
    else:
        print("   ❌ Environment test failed")
        return
    
    # 2. 创建测试数据
    print("\n2. Creating test data...")
    test_csv_path = PROJECT_ROOT / "data" / "processed" / "comprehensive_test.csv"
    
    test_data = {
        "product": ["cola", "sprite", "cola", "sprite", "fanta", "cola", "sprite", "fanta"],
        "sales": [100, 150, 120, 180, 90, 110, 160, 95],
        "quantity": [10, 15, 12, 18, 9, 11, 16, 10],
        "month": ["Jan", "Jan", "Feb", "Feb", "Jan", "Mar", "Mar", "Feb"]
    }
    
    df = pd.DataFrame(test_data)
    df.to_csv(test_csv_path, index=False, encoding='utf-8')
    print(f"   ✅ Test data created: {len(df)} rows")
    
    # 3. 基础功能测试
    print("\n3. Testing basic functionality...")
    basic_code = """
# Basic data analysis
df = pd.read_csv(CSV_FILE_PATH)
print("Dataset Info:")
print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print("\\nFirst 3 rows:")
print(df.head(3))
print("\\nData types:")
print(df.dtypes)
"""
    
    result = await test_code_execution("Basic functionality", basic_code, test_csv_path)
    
    # 4. 统计分析测试
    print("\n4. Testing statistical analysis...")
    stats_code = """
# Statistical analysis
df = pd.read_csv(CSV_FILE_PATH)

print("=== Statistical Summary ===")
print(df.describe())

print("\\n=== Product Analysis ===")
product_stats = df.groupby('product').agg({
    'sales': ['sum', 'mean', 'count'],
    'quantity': ['sum', 'mean']
}).round(2)
print(product_stats)

print("\\n=== Monthly Trends ===")
monthly_stats = df.groupby('month')['sales'].sum().sort_values(ascending=False)
print(monthly_stats)
"""
    
    result = await test_code_execution("Statistical analysis", stats_code, test_csv_path)
    
    # 5. 数据可视化测试
    print("\n5. Testing data visualization...")
    viz_code = """
# Data visualization
df = pd.read_csv(CSV_FILE_PATH)

# Create multiple charts
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))

# 1. Sales by product (bar chart)
product_sales = df.groupby('product')['sales'].sum()
ax1.bar(product_sales.index, product_sales.values, color='skyblue')
ax1.set_title('Total Sales by Product')
ax1.set_xlabel('Product')
ax1.set_ylabel('Sales')
ax1.tick_params(axis='x', rotation=45)

# 2. Monthly trends (line chart)
monthly_sales = df.groupby('month')['sales'].sum()
ax2.plot(monthly_sales.index, monthly_sales.values, marker='o', linewidth=2)
ax2.set_title('Monthly Sales Trend')
ax2.set_xlabel('Month')
ax2.set_ylabel('Sales')
ax2.grid(True, alpha=0.3)

# 3. Sales vs Quantity scatter plot
ax3.scatter(df['quantity'], df['sales'], alpha=0.6, color='green')
ax3.set_title('Sales vs Quantity')
ax3.set_xlabel('Quantity')
ax3.set_ylabel('Sales')
ax3.grid(True, alpha=0.3)

# 4. Product distribution (pie chart)
product_counts = df['product'].value_counts()
ax4.pie(product_counts.values, labels=product_counts.index, autopct='%1.1f%%')
ax4.set_title('Product Distribution')

plt.tight_layout()
plt.savefig(OUTPUT_IMAGE_PATH, dpi=300, bbox_inches='tight')

print("Visualization completed successfully!")
print(f"Product sales: {product_sales.to_dict()}")
print(f"Monthly sales: {monthly_sales.to_dict()}")
"""
    
    result = await test_code_execution("Data visualization", viz_code, test_csv_path)
    
    # 6. 高级分析测试
    print("\n6. Testing advanced analysis...")
    advanced_code = """
# Advanced analysis
df = pd.read_csv(CSV_FILE_PATH)

# Data preprocessing
df['sales_per_unit'] = df['sales'] / df['quantity']
df['month_num'] = df['month'].map({'Jan': 1, 'Feb': 2, 'Mar': 3})

# Correlation analysis
correlation = df[['sales', 'quantity', 'sales_per_unit', 'month_num']].corr()
print("=== Correlation Matrix ===")
print(correlation)

# Top performers
top_products = df.groupby('product')['sales'].sum().nlargest(3)
print("\\n=== Top 3 Products ===")
for product, sales in top_products.items():
    print(f"{product}: {sales}")

# Growth analysis
monthly_growth = df.groupby('month')['sales'].sum().pct_change() * 100
print("\\n=== Monthly Growth Rate ===")
print(monthly_growth.dropna())

# Performance metrics
total_sales = df['sales'].sum()
avg_sales_per_product = df.groupby('product')['sales'].sum().mean()
print(f"\\n=== Performance Metrics ===")
print(f"Total Sales: {total_sales}")
print(f"Average Sales per Product: {avg_sales_per_product:.2f}")
print(f"Total Products: {df['product'].nunique()}")
print(f"Total Months: {df['month'].nunique()}")
"""
    
    result = await test_code_execution("Advanced analysis", advanced_code, test_csv_path)
    
    print("\n🎉 Comprehensive test completed!")
    print("=" * 60)


async def test_code_execution(test_name, code, csv_path):
    """测试代码执行"""
    try:
        result = await virtualenv_code_executor.execute_code(code, str(csv_path))
        
        if result.success:
            print(f"   ✅ {test_name} successful")
            print(f"   Output length: {len(result.output)} characters")
            
            if result.image:
                print("   ✅ Chart generated")
                # Save image
                output_dir = PROJECT_ROOT / "data" / "output"
                output_dir.mkdir(exist_ok=True)
                
                import base64
                image_data = base64.b64decode(result.image)
                image_path = output_dir / f"test_{test_name.lower().replace(' ', '_')}.png"
                with open(image_path, 'wb') as f:
                    f.write(image_data)
                print(f"   📊 Chart saved: {image_path}")
            else:
                print("   ℹ️  No chart generated")
                
            # Show sample output
            if len(result.output) > 0:
                lines = result.output.split('\\n')[:5]  # Show first 5 lines
                print("   Sample output:")
                for line in lines:
                    if line.strip():
                        print(f"     {line}")
        else:
            print(f"   ❌ {test_name} failed: {result.error}")
            
    except Exception as e:
        print(f"   ❌ {test_name} exception: {e}")


if __name__ == "__main__":
    asyncio.run(test_comprehensive())

