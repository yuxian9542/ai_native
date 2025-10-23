#!/usr/bin/env python3
"""
代码生成和执行测试
测试Python代码生成、执行和图表生成功能
"""
import sys
import asyncio
import pandas as pd
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.services.code_generator import code_generator
from backend.services.code_executor import code_executor
from backend.models.schemas import FileSearchResult, ColumnInfo


async def test_code_generation_and_execution():
    """测试代码生成和执行"""
    print("💻 代码生成和执行测试")
    print("=" * 50)
    
    # 1. 创建测试数据
    print("1. 创建测试数据...")
    test_csv_path = PROJECT_ROOT / "data" / "processed" / "test_code_execution.csv"
    
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
    
    # 2. 创建模拟文件信息
    print("2. 创建模拟文件信息...")
    mock_file = FileSearchResult(
        file_id="test_code_execution",
        file_name="test_sales_data.xlsx",
        summary="测试销售数据，包含产品名称、销售额、数量和月份信息",
        score=0.95,
        columns=[
            ColumnInfo(
                name="产品名称",
                type="object",
                description="产品名称",
                sample_values=["可乐", "雪碧", "芬达"],
                unique_count=3,
                null_count=0
            ),
            ColumnInfo(
                name="销售额",
                type="float64",
                description="销售金额",
                sample_values=["100.0", "150.0", "90.0"],
                unique_count=10,
                null_count=0
            ),
            ColumnInfo(
                name="数量",
                type="int64",
                description="销售数量",
                sample_values=["10", "15", "9"],
                unique_count=10,
                null_count=0
            ),
            ColumnInfo(
                name="月份",
                type="object",
                description="销售月份",
                sample_values=["1月", "2月", "3月"],
                unique_count=4,
                null_count=0
            )
        ]
    )
    print("   ✅ 模拟文件信息已创建")
    
    # 3. 测试不同的分析问题
    test_questions = [
        "统计各产品的总销售额",
        "计算各产品的平均销售额",
        "按月份统计销售趋势",
        "生成销售额的柱状图",
        "分析哪个产品销量最好"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n3.{i} 测试问题: {question}")
        
        try:
            # 生成代码
            print("   生成分析代码...")
            code_result = await code_generator.generate_code(question, mock_file)
            
            print(f"   ✅ 代码生成成功")
            print(f"   分析类型: {code_result.analysis_type}")
            print(f"   使用列: {', '.join(code_result.used_columns)}")
            
            # 执行代码
            print("   执行分析代码...")
            exec_result = await code_executor.execute_code(code_result.code, str(test_csv_path))
            
            if exec_result.success:
                print("   ✅ 代码执行成功")
                print(f"   输出长度: {len(exec_result.output)} 字符")
                
                # 显示部分输出
                output_preview = exec_result.output[:200] + "..." if len(exec_result.output) > 200 else exec_result.output
                print(f"   输出预览: {output_preview}")
                
                # 检查是否生成了图片
                if exec_result.image:
                    print("   ✅ 图表生成成功")
                else:
                    print("   ℹ️  未生成图表")
                    
            else:
                print(f"   ❌ 代码执行失败: {exec_result.error}")
                
        except Exception as e:
            print(f"   ❌ 测试失败: {e}")
    
    # 4. 测试复杂分析
    print(f"\n4. 测试复杂分析...")
    complex_question = "分析销售数据，按产品分组统计总销售额和平均数量，并生成对比柱状图"
    
    try:
        print("   生成复杂分析代码...")
        code_result = await code_generator.generate_code(complex_question, mock_file)
        
        print("   执行复杂分析...")
        exec_result = await code_executor.execute_code(code_result.code, str(test_csv_path))
        
        if exec_result.success:
            print("   ✅ 复杂分析执行成功")
            print(f"   输出长度: {len(exec_result.output)} 字符")
            
            if exec_result.image:
                print("   ✅ 复杂图表生成成功")
                
                # 保存图片到输出目录
                output_dir = PROJECT_ROOT / "data" / "output"
                output_dir.mkdir(exist_ok=True)
                
                import base64
                image_data = base64.b64decode(exec_result.image)
                image_path = output_dir / "test_complex_analysis.png"
                with open(image_path, 'wb') as f:
                    f.write(image_data)
                print(f"   📊 图表已保存: {image_path}")
        else:
            print(f"   ❌ 复杂分析失败: {exec_result.error}")
            
    except Exception as e:
        print(f"   ❌ 复杂分析测试失败: {e}")
    
    print("\n🎉 代码生成和执行测试完成！")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(test_code_generation_and_execution())
