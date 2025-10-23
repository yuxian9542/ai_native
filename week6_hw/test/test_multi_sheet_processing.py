#!/usr/bin/env python3
"""
测试多工作表Excel处理功能
"""
import sys
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.excel_processor import excel_processor
from backend.config import settings

async def test_multi_sheet_processing():
    """测试多工作表Excel处理"""
    print("🧪 测试多工作表Excel处理功能")
    
    # 测试文件路径
    test_file = Path(__file__).parent / "data" / "original" / "test_multi_sheet.xlsx"
    output_file = Path(__file__).parent / "data" / "processed" / "test_multi_sheet_processed.xlsx"
    
    # 创建测试文件（如果不存在）
    if not test_file.exists():
        print("📝 创建测试多工作表Excel文件...")
        import pandas as pd
        
        # 创建多个工作表
        with pd.ExcelWriter(str(test_file), engine='openpyxl') as writer:
            # 工作表1：销售数据
            sales_data = {
                '产品名称': ['产品A', '产品B', '产品C'],
                '销售额': [1000, 2000, 1500],
                '数量': [10, 20, 15]
            }
            df1 = pd.DataFrame(sales_data)
            df1.to_excel(writer, sheet_name='销售数据', index=False)
            
            # 工作表2：客户信息
            customer_data = {
                '客户ID': [1, 2, 3],
                '客户名称': ['客户A', '客户B', '客户C'],
                '联系方式': ['123-456-7890', '098-765-4321', '555-123-4567']
            }
            df2 = pd.DataFrame(customer_data)
            df2.to_excel(writer, sheet_name='客户信息', index=False)
            
            # 工作表3：财务数据
            financial_data = {
                '月份': ['1月', '2月', '3月'],
                '收入': [50000, 60000, 55000],
                '支出': [30000, 35000, 32000]
            }
            df3 = pd.DataFrame(financial_data)
            df3.to_excel(writer, sheet_name='财务数据', index=False)
        
        print(f"✅ 测试文件已创建: {test_file}")
    
    try:
        # 处理Excel文件
        print(f"🔄 开始处理Excel文件: {test_file}")
        result = await excel_processor.process_excel(str(test_file), str(output_file))
        
        print("📊 处理结果:")
        print(f"  - 总工作表数: {result.get('total_sheets', 0)}")
        print(f"  - 成功处理: {result.get('processed_sheets', 0)}")
        print(f"  - 总行数: {result.get('final_rows', 0)}")
        print(f"  - 最大列数: {result.get('final_columns', 0)}")
        
        # 显示每个工作表的详细信息
        if 'processed_sheets_info' in result:
            print("\n📋 工作表详情:")
            for sheet_name, info in result['processed_sheets_info'].items():
                status = "✅" if info['status'] == 'success' else "❌"
                print(f"  {status} {sheet_name}: {info['rows']}行 × {info['columns']}列")
                if info['status'] == 'error':
                    print(f"    错误: {info.get('error', '未知错误')}")
        
        # 验证输出文件
        if output_file.exists():
            print(f"\n✅ 输出文件已生成: {output_file}")
            
            # 读取输出文件验证
            import pandas as pd
            excel_file = pd.ExcelFile(str(output_file))
            print(f"📊 输出文件包含 {len(excel_file.sheet_names)} 个工作表:")
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(str(output_file), sheet_name=sheet_name)
                print(f"  - {sheet_name}: {len(df)}行 × {len(df.columns)}列")
                print(f"    列名: {list(df.columns)}")
        else:
            print("❌ 输出文件未生成")
            
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()

async def test_single_sheet_processing():
    """测试单工作表Excel处理（向后兼容）"""
    print("\n🧪 测试单工作表Excel处理功能")
    
    # 使用现有的测试文件
    test_file = Path(__file__).parent / "data" / "original" / "test_data.xlsx"
    output_file = Path(__file__).parent / "data" / "processed" / "test_single_sheet_processed.xlsx"
    
    if not test_file.exists():
        print("⚠️ 测试文件不存在，跳过单工作表测试")
        return
    
    try:
        print(f"🔄 开始处理单工作表Excel文件: {test_file}")
        result = await excel_processor.process_excel(str(test_file), str(output_file))
        
        print("📊 处理结果:")
        print(f"  - 跳过的行数: {result.get('skipped_rows', 0)}")
        print(f"  - 表头行号: {result.get('header_row', 0)}")
        print(f"  - 合并单元格数: {result.get('merged_cells_count', 0)}")
        print(f"  - 最终行数: {result.get('final_rows', 0)}")
        print(f"  - 最终列数: {result.get('final_columns', 0)}")
        
        if output_file.exists():
            print(f"✅ 输出文件已生成: {output_file}")
        else:
            print("❌ 输出文件未生成")
            
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """主测试函数"""
    print("🚀 开始多工作表Excel处理测试")
    
    # 确保数据目录存在
    Path(__file__).parent / "data" / "original" / "original"
    Path(__file__).parent / "data" / "processed" / "processed"
    
    # 运行测试
    await test_multi_sheet_processing()
    await test_single_sheet_processing()
    
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    asyncio.run(main())
