#!/usr/bin/env python3
"""
调试代码生成问题
"""
import sys
import asyncio
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.utils.openai_client import openai_client
from backend.models.schemas import FileSearchResult, ColumnInfo


async def debug_code_generation():
    """调试代码生成"""
    print("🔍 调试代码生成问题")
    print("=" * 50)
    
    # 创建简单的测试数据
    mock_file = FileSearchResult(
        file_id="test_id",
        file_name="test_file.xlsx",
        summary="测试销售数据",
        score=0.95,
        columns=[
            ColumnInfo(
                name="产品名称",
                type="object",
                description="产品名称",
                sample_values=["可乐", "雪碧"],
                unique_count=10,
                null_count=0
            ),
            ColumnInfo(
                name="销售额",
                type="float64",
                description="销售金额",
                sample_values=["100.0", "200.0"],
                unique_count=50,
                null_count=0
            )
        ]
    )
    
    # 测试简单的代码生成请求
    question = "统计各产品的总销售额"
    
    # 构建提示词
    prompt = f"""
请为以下问题生成Python分析代码：

问题：{question}

文件信息：
- 文件名：{mock_file.file_name}
- 摘要：{mock_file.summary}
- 列信息：
"""
    
    for col in mock_file.columns:
        prompt += f"  - {col.name} ({col.type}): {col.description}\n"
    
    prompt += """
请生成一个JSON格式的响应，包含以下字段：
- code: Python代码字符串
- used_columns: 使用的列名列表
- analysis_type: 分析类型

代码要求：
1. 使用pandas读取CSV文件
2. 使用CSV_FILE_PATH变量作为文件路径
3. 使用OUTPUT_IMAGE_PATH变量作为图片保存路径
4. 生成适当的图表
5. 输出分析结果
"""
    
    messages = [
        {
            "role": "system", 
            "content": "你是一个专业的数据分析助手，能够根据用户问题生成Python分析代码。请始终以JSON格式回复。"
        },
        {"role": "user", "content": prompt}
    ]
    
    try:
        print("1. 发送请求到OpenAI...")
        response = await openai_client.chat_completion(
            messages,
            model="gpt-4",
            temperature=0.2,
            max_tokens=2000
        )
        
        print("2. 收到响应:")
        print("-" * 30)
        print(response)
        print("-" * 30)
        
        print("3. 尝试提取JSON...")
        try:
            result_json = openai_client.extract_json(response)
            print("✅ JSON提取成功:")
            print(result_json)
        except Exception as e:
            print(f"❌ JSON提取失败: {e}")
            
            # 尝试手动解析
            print("\n4. 尝试手动解析...")
            import re
            import json
            
            # 查找JSON代码块
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                print("找到JSON代码块:")
                print(json_match.group(1))
                try:
                    result = json.loads(json_match.group(1))
                    print("✅ 手动解析成功:")
                    print(result)
                except Exception as e2:
                    print(f"❌ 手动解析失败: {e2}")
            
            # 查找大括号内容
            brace_match = re.search(r'\{.*\}', response, re.DOTALL)
            if brace_match:
                print("找到大括号内容:")
                print(brace_match.group(0))
                try:
                    result = json.loads(brace_match.group(0))
                    print("✅ 大括号解析成功:")
                    print(result)
                except Exception as e3:
                    print(f"❌ 大括号解析失败: {e3}")
        
    except Exception as e:
        print(f"❌ 请求失败: {e}")


if __name__ == "__main__":
    asyncio.run(debug_code_generation())

