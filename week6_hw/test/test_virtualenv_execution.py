#!/usr/bin/env python3
"""
虚拟环境代码执行测试
测试在虚拟环境中执行Python代码的功能
"""
import sys
import asyncio
import pandas as pd
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.services.virtualenv_code_executor import virtualenv_code_executor
from backend.models.schemas import FileSearchResult, ColumnInfo


async def test_virtualenv_execution():
    """测试虚拟环境代码执行"""
    print("🐍 虚拟环境代码执行测试")
    print("=" * 50)
    
    # 1. 测试环境
    print("1. 测试执行环境...")
    if virtualenv_code_executor.test_environment():
        print("   ✅ 虚拟环境执行环境正常")
    else:
        print("   ❌ 虚拟环境执行环境异常")
        return
    
    # 2. 创建测试数据
    print("\n2. 创建测试数据...")
    test_csv_path = PROJECT_ROOT / "data" / "processed" / "test_virtualenv_execution.csv"
    
    # 生成测试数据
    test_data = {
        "产品名称": ["可乐", "雪碧", "可乐", "雪碧", "芬达", "可乐", "雪碧", "芬达", "可乐", "雪碧"],
        "销售额": [100, 150, 120, 180, 90, 110, 160, 95, 130, 170],
        "数量": [10, 15, 12, 18, 9, 11, 16, 10, 13, 17],
        "月份": ["1月", "1月", "2月", "2月", "1月", "3月", "3月", "2月", "4月", "4月"]
    }
    
    df = pd.DataFrame(test_data)
    df.to_csv(test_csv_path, index=False, encoding='utf-8-sig')
    print(f"   ✅ 测试数据已创建: {len(df)} 行数据")
    
    # 3. 测试简单代码执行
    print("\n3. 测试简单代码执行...")
    simple_code = """
# Read data
df = pd.read_csv(CSV_FILE_PATH)
print("Data shape:", df.shape)
print("Column names:", list(df.columns))
print("First 3 rows:")
print(df.head(3))
"""
    
    try:
        result = await virtualenv_code_executor.execute_code(simple_code, str(test_csv_path))
        
        if result.success:
            print("   ✅ 简单代码执行成功")
            print(f"   输出长度: {len(result.output)} 字符")
            print("   输出内容:")
            print(result.output[:200] + "..." if len(result.output) > 200 else result.output)
        else:
            print(f"   ❌ 简单代码执行失败: {result.error}")
            
    except Exception as e:
        print(f"   ❌ 简单代码执行异常: {e}")
    
    # 4. 测试数据分析代码
    print("\n4. 测试数据分析代码...")
    analysis_code = """
# 读取数据
df = pd.read_csv(CSV_FILE_PATH)

# 基本统计
print("=== 基本统计信息 ===")
print(df.describe())

# 按产品分组统计
print("\\n=== 按产品分组统计 ===")
product_stats = df.groupby('产品名称').agg({
    '销售额': ['sum', 'mean', 'count'],
    '数量': ['sum', 'mean']
}).round(2)
print(product_stats)

# 按月份统计
print("\\n=== 按月份统计 ===")
monthly_stats = df.groupby('月份')['销售额'].sum()
print(monthly_stats)
"""
    
    try:
        result = await virtualenv_code_executor.execute_code(analysis_code, str(test_csv_path))
        
        if result.success:
            print("   ✅ 数据分析代码执行成功")
            print(f"   输出长度: {len(result.output)} 字符")
        else:
            print(f"   ❌ 数据分析代码执行失败: {result.error}")
            
    except Exception as e:
        print(f"   ❌ 数据分析代码执行异常: {e}")
    
    # 5. 测试图表生成代码
    print("\n5. 测试图表生成代码...")
    chart_code = """
# 读取数据
df = pd.read_csv(CSV_FILE_PATH)

# 创建图表
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# 销售额柱状图
sales_by_product = df.groupby('产品名称')['销售额'].sum()
ax1.bar(sales_by_product.index, sales_by_product.values, color='skyblue')
ax1.set_title('各产品总销售额')
ax1.set_xlabel('产品名称')
ax1.set_ylabel('销售额')
ax1.tick_params(axis='x', rotation=45)

# 数量折线图
quantity_by_month = df.groupby('月份')['数量'].sum()
ax2.plot(quantity_by_month.index, quantity_by_month.values, marker='o', color='red')
ax2.set_title('各月份销售数量趋势')
ax2.set_xlabel('月份')
ax2.set_ylabel('数量')
ax2.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig(OUTPUT_IMAGE_PATH, dpi=300, bbox_inches='tight')

print("图表已生成并保存")
print(f"销售额统计: {sales_by_product.to_dict()}")
print(f"数量统计: {quantity_by_month.to_dict()}")
"""
    
    try:
        result = await virtualenv_code_executor.execute_code(chart_code, str(test_csv_path))
        
        if result.success:
            print("   ✅ 图表生成代码执行成功")
            print(f"   输出长度: {len(result.output)} 字符")
            
            if result.image:
                print("   ✅ 图表生成成功")
                # 保存图片到输出目录
                output_dir = PROJECT_ROOT / "data" / "output"
                output_dir.mkdir(exist_ok=True)
                
                import base64
                image_data = base64.b64decode(result.image)
                image_path = output_dir / "test_virtualenv_chart.png"
                with open(image_path, 'wb') as f:
                    f.write(image_data)
                print(f"   📊 图表已保存: {image_path}")
            else:
                print("   ⚠️  未生成图表")
        else:
            print(f"   ❌ 图表生成代码执行失败: {result.error}")
            
    except Exception as e:
        print(f"   ❌ 图表生成代码执行异常: {e}")
    
    # 6. 测试复杂分析代码
    print("\n6. 测试复杂分析代码...")
    complex_code = """
# 读取数据
df = pd.read_csv(CSV_FILE_PATH)

# 数据预处理
df['销售额'] = pd.to_numeric(df['销售额'], errors='coerce')
df['数量'] = pd.to_numeric(df['数量'], errors='coerce')
df = df.dropna()

# 计算指标
df['单价'] = df['销售额'] / df['数量']
df['销售额占比'] = df['销售额'] / df['销售额'].sum() * 100

# 创建综合图表
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

# 1. 销售额分布
ax1.hist(df['销售额'], bins=10, alpha=0.7, color='blue')
ax1.set_title('销售额分布直方图')
ax1.set_xlabel('销售额')
ax1.set_ylabel('频次')

# 2. 产品销售额对比
product_sales = df.groupby('产品名称')['销售额'].sum()
ax2.pie(product_sales.values, labels=product_sales.index, autopct='%1.1f%%')
ax2.set_title('产品销售额占比')

# 3. 单价vs数量散点图
ax3.scatter(df['数量'], df['单价'], alpha=0.6, color='green')
ax3.set_title('数量与单价关系')
ax3.set_xlabel('数量')
ax3.set_ylabel('单价')

# 4. 月份趋势
monthly_trend = df.groupby('月份')['销售额'].sum()
ax4.plot(monthly_trend.index, monthly_trend.values, marker='o', linewidth=2, markersize=8)
ax4.set_title('月度销售额趋势')
ax4.set_xlabel('月份')
ax4.set_ylabel('销售额')
ax4.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig(OUTPUT_IMAGE_PATH, dpi=300, bbox_inches='tight')

# 输出分析结果
print("=== 综合分析结果 ===")
print(f"总销售额: {df['销售额'].sum():.2f}")
print(f"平均单价: {df['单价'].mean():.2f}")
print(f"最畅销产品: {product_sales.idxmax()}")
print(f"最高单价: {df['单价'].max():.2f}")
print(f"数据质量: {len(df)} 条有效记录")
"""
    
    try:
        result = await virtualenv_code_executor.execute_code(complex_code, str(test_csv_path))
        
        if result.success:
            print("   ✅ 复杂分析代码执行成功")
            print(f"   输出长度: {len(result.output)} 字符")
            
            if result.image:
                print("   ✅ 复杂图表生成成功")
                # 保存图片
                output_dir = PROJECT_ROOT / "data" / "output"
                output_dir.mkdir(exist_ok=True)
                
                import base64
                image_data = base64.b64decode(result.image)
                image_path = output_dir / "test_virtualenv_complex_analysis.png"
                with open(image_path, 'wb') as f:
                    f.write(image_data)
                print(f"   📊 复杂图表已保存: {image_path}")
            else:
                print("   ⚠️  未生成复杂图表")
        else:
            print(f"   ❌ 复杂分析代码执行失败: {result.error}")
            
    except Exception as e:
        print(f"   ❌ 复杂分析代码执行异常: {e}")
    
    print("\n🎉 虚拟环境代码执行测试完成！")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(test_virtualenv_execution())
