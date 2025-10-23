#!/usr/bin/env python3
"""
测试JSON解析功能
"""
import sys
import json
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.utils.openai_client import openai_client


def test_json_parsing():
    """测试JSON解析"""
    print("🔍 测试JSON解析功能")
    print("=" * 50)
    
    # 测试用例1：简单的JSON
    test_json1 = '{"code": "print(\'hello\')", "used_columns": ["col1"], "analysis_type": "test"}'
    print("1. 测试简单JSON:")
    print(f"输入: {test_json1}")
    try:
        result1 = openai_client.extract_json(test_json1)
        print(f"✅ 解析成功: {result1}")
    except Exception as e:
        print(f"❌ 解析失败: {e}")
    
    # 测试用例2：包含换行符的JSON
    test_json2 = '''{
    "code": "import pandas as pd\\nprint('hello')",
    "used_columns": ["col1", "col2"],
    "analysis_type": "test"
}'''
    print("\n2. 测试包含换行符的JSON:")
    print(f"输入: {test_json2}")
    try:
        result2 = openai_client.extract_json(test_json2)
        print(f"✅ 解析成功: {result2}")
    except Exception as e:
        print(f"❌ 解析失败: {e}")
    
    # 测试用例3：实际GPT响应格式
    test_json3 = '''{
    "code": "
import pandas as pd
import numpy as np

# 读取数据
df = pd.read_excel(CSV_FILE_PATH)

# 处理可能的空值和异常
df = df.dropna()

# 计算各产品的总销售额
product_sales = df.groupby('产品名称')['销售额'].sum()

# 输出结果
print(product_sales)
    ",
    "used_columns": ["产品名称", "销售额"],
    "analysis_type": "统计汇总",
    "expected_output": "一个Series，索引为产品名称，值为对应的总销售额"
}'''
    print("\n3. 测试实际GPT响应格式:")
    print(f"输入长度: {len(test_json3)} 字符")
    try:
        result3 = openai_client.extract_json(test_json3)
        print(f"✅ 解析成功: {result3}")
        print(f"代码长度: {len(result3.get('code', ''))}")
    except Exception as e:
        print(f"❌ 解析失败: {e}")
        
        # 尝试手动解析
        print("\n4. 尝试手动解析:")
        try:
            # 直接使用json.loads
            manual_result = json.loads(test_json3)
            print(f"✅ 手动解析成功: {manual_result}")
        except Exception as e2:
            print(f"❌ 手动解析也失败: {e2}")
            
            # 尝试修复JSON
            print("\n5. 尝试修复JSON:")
            try:
                # 移除多余的空白字符
                cleaned = test_json3.strip()
                fixed_result = json.loads(cleaned)
                print(f"✅ 修复后解析成功: {fixed_result}")
            except Exception as e3:
                print(f"❌ 修复后仍然失败: {e3}")


if __name__ == "__main__":
    test_json_parsing()

