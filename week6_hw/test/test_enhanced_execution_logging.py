#!/usr/bin/env python3
"""
测试增强的执行日志和错误显示功能
"""
import sys
from pathlib import Path
import pandas as pd
import asyncio

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.virtualenv_code_executor import virtualenv_code_executor
from backend.utils.logger import logger


async def test_detailed_execution_logging():
    """测试详细的执行日志"""
    print("📊 Testing Detailed Execution Logging")
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
    test_file = Path('data/processed/test_execution_logging.xlsx').resolve()
    test_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(test_file, index=False)
    print(f"   ✅ Test file created: {test_file}")
    
    # 2. 测试成功执行的详细日志
    print("\n2. Testing successful execution with detailed logging...")
    success_code = """
# 成功执行的代码
print("开始分析产品销量数据...")
print(f"数据形状: {df.shape}")
print(f"列名: {list(df.columns)}")

# 基本统计
print("\\n=== 基本统计信息 ===")
print(df.describe())

# 按产品统计销量
print("\\n=== 按产品统计销量 ===")
product_sales = df.groupby('product')['sales'].sum().sort_values(ascending=False)
print(product_sales)

# 生成图表
import matplotlib.pyplot as plt
plt.figure(figsize=(10, 6))
product_sales.plot(kind='bar')
plt.title('产品销量统计')
plt.xlabel('产品')
plt.ylabel('销量')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('output.png')
print("\\n图表已保存为 output.png")
print("\\n分析完成！")
"""
    
    try:
        result = await virtualenv_code_executor.execute_code(success_code, str(test_file))
        print(f"   ✅ Execution result: {result.success}")
        if result.success:
            print(f"   📤 Output length: {len(result.output)}")
            print(f"   🖼️ Image generated: {result.image is not None}")
            print(f"   📄 Output preview: {result.output[:200]}...")
        else:
            print(f"   ❌ Error: {result.error}")
    except Exception as e:
        print(f"   💥 Exception: {e}")
    
    # 3. 测试失败执行的详细错误信息
    print("\n3. Testing failed execution with detailed error logging...")
    error_code = """
# 故意制造错误的代码
print("开始分析...")

# 使用不存在的列名
result = df['nonexistent_column'].sum()
print(f"结果: {result}")

# 使用不存在的变量
print(undefined_variable)

# 语法错误
if True
    print("这行有语法错误")
"""
    
    try:
        result = await virtualenv_code_executor.execute_code(error_code, str(test_file))
        print(f"   📊 Execution result: {result.success}")
        if not result.success:
            print(f"   ❌ Error captured:")
            print(f"   📄 Error details: {result.error}")
        else:
            print(f"   ✅ Unexpected success: {result.output}")
    except Exception as e:
        print(f"   💥 Exception: {e}")
    
    # 4. 测试编码问题的处理
    print("\n4. Testing encoding issue handling...")
    encoding_code = """
# 测试中文字符处理
print("测试中文字符: 你好世界")
print("测试特殊字符: !@#$%^&*()")
print("测试Unicode: 🚀📊💻")

# 测试数据中的中文字符
df_test = pd.DataFrame({'中文列': ['测试', '数据', '分析']})
print(f"中文列数据: {df_test['中文列'].tolist()}")
"""
    
    try:
        result = await virtualenv_code_executor.execute_code(encoding_code, str(test_file))
        print(f"   📊 Execution result: {result.success}")
        if result.success:
            print(f"   📤 Output: {result.output}")
        else:
            print(f"   ❌ Error: {result.error}")
    except Exception as e:
        print(f"   💥 Exception: {e}")


async def test_retry_simulation():
    """测试重试逻辑模拟"""
    print("\n🔄 Testing Retry Logic Simulation")
    print("=" * 50)
    
    # 创建测试文件
    test_data = {
        'product': ['cola', 'sprite', 'fanta'],
        'sales': [100, 150, 90],
        'quantity': [10, 15, 9]
    }
    
    df = pd.DataFrame(test_data)
    test_file = Path('data/processed/test_retry_simulation.xlsx').resolve()
    test_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(test_file, index=False)
    
    # 模拟重试逻辑
    max_retries = 3
    last_error = None
    
    for attempt in range(max_retries):
        print(f"\n--- 第 {attempt + 1} 次尝试 ---")
        
        if attempt == 0:
            # 第一次尝试 - 使用错误的列名
            code = """
# 第一次尝试 - 使用错误的列名
result = df['wrong_column'].sum()
print(f"结果: {result}")
"""
        elif attempt == 1:
            # 第二次尝试 - 修正列名但使用错误的方法
            code = """
# 第二次尝试 - 修正列名但使用错误的方法
result = df['product'].sum()  # product是字符串列，不能sum
print(f"结果: {result}")
"""
        else:
            # 第三次尝试 - 正确的代码
            code = """
# 第三次尝试 - 正确的代码
result = df['sales'].sum()
print(f"销量总和: {result}")

# 按产品统计
product_stats = df.groupby('product')['sales'].sum()
print(f"按产品统计: {product_stats.to_dict()}")
"""
        
        try:
            result = await virtualenv_code_executor.execute_code(code, str(test_file))
            
            if result.success:
                print(f"   ✅ 第 {attempt + 1} 次尝试成功!")
                print(f"   📤 输出: {result.output}")
                break
            else:
                last_error = result.error
                print(f"   ❌ 第 {attempt + 1} 次尝试失败")
                print(f"   📄 错误信息: {last_error[:300]}...")
                
                if attempt < max_retries - 1:
                    print(f"   🔄 准备第 {attempt + 2} 次重试...")
                else:
                    print(f"   💥 达到最大重试次数 {max_retries}")
                    
        except Exception as e:
            last_error = str(e)
            print(f"   💥 第 {attempt + 1} 次尝试异常: {e}")
            
            if attempt < max_retries - 1:
                print(f"   🔄 准备第 {attempt + 2} 次重试...")
            else:
                print(f"   💥 达到最大重试次数 {max_retries}")


async def main():
    """主测试函数"""
    print("🧪 Testing Enhanced Execution Logging and Error Display")
    print("=" * 70)
    
    try:
        # 测试详细执行日志
        await test_detailed_execution_logging()
        
        # 测试重试逻辑模拟
        await test_retry_simulation()
        
        print("\n🎉 All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
