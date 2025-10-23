#!/usr/bin/env python3
"""
测试详细错误处理
直接测试代码执行器的错误捕获功能
"""
import sys
from pathlib import Path
import pandas as pd
import asyncio

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.virtualenv_code_executor import virtualenv_code_executor


async def test_detailed_error_handling():
    """测试详细错误处理"""
    print("🔧 Testing Detailed Error Handling")
    print("=" * 50)
    
    # 1. 创建测试文件
    print("1. Creating test file...")
    test_data = {
        'product': ['cola', 'sprite', 'fanta'],
        'sales': [100, 150, 90],
        'quantity': [10, 15, 9]
    }
    
    df = pd.DataFrame(test_data)
    test_file = Path('data/processed/test_error_handling.xlsx').resolve()
    test_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(test_file, index=False)
    print(f"   ✅ Test file created: {test_file}")
    
    # 2. 测试有错误的代码
    print("2. Testing code with errors...")
    error_code = """
# 故意制造错误
print("开始分析...")

# 尝试访问不存在的列
result = df['nonexistent_column'].sum()
print(f"结果: {result}")

# 尝试除以零
division_result = 10 / 0
print(f"除法结果: {division_result}")
"""
    
    try:
        result = await virtualenv_code_executor.execute_code(error_code, str(test_file))
        print(f"   📊 Execution result: {result.success}")
        if result.success:
            print(f"   📤 Output: {result.output}")
        else:
            print(f"   ❌ Error: {result.error}")
    except Exception as e:
        print(f"   💥 Exception: {e}")
    
    # 3. 测试语法错误
    print("3. Testing syntax error...")
    syntax_error_code = """
# 语法错误
print("开始分析...")
if True
    print("这行有语法错误")
"""
    
    try:
        result = await virtualenv_code_executor.execute_code(syntax_error_code, str(test_file))
        print(f"   📊 Execution result: {result.success}")
        if result.success:
            print(f"   📤 Output: {result.output}")
        else:
            print(f"   ❌ Error: {result.error}")
    except Exception as e:
        print(f"   💥 Exception: {e}")
    
    # 4. 测试导入错误
    print("4. Testing import error...")
    import_error_code = """
# 导入不存在的模块
import nonexistent_module

print("这行不会执行")
"""
    
    try:
        result = await virtualenv_code_executor.execute_code(import_error_code, str(test_file))
        print(f"   📊 Execution result: {result.success}")
        if result.success:
            print(f"   📤 Output: {result.output}")
        else:
            print(f"   ❌ Error: {result.error}")
    except Exception as e:
        print(f"   💥 Exception: {e}")
    
    print("\\n🎉 Error handling test completed!")


if __name__ == "__main__":
    asyncio.run(test_detailed_error_handling())
