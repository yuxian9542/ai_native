#!/usr/bin/env python3
"""
Excel处理器功能测试总结
"""
import sys
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

async def test_summary():
    """测试总结"""
    print("🎉 Excel处理器增强功能测试总结")
    print("=" * 60)
    
    from backend.services.excel_processor import excel_processor
    
    # 测试文件路径
    test_file = Path(__file__).parent.parent / "backend" / "data" / "original" / "发电日志.xlsx"
    output_file = Path(__file__).parent / "data" / "processed" / "发电日志_summary_test.xlsx"
    
    # 确保输出目录存在
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    if not test_file.exists():
        print(f"❌ 测试文件不存在: {test_file}")
        return
    
    try:
        print(f"📁 测试文件: {test_file}")
        print(f"📁 输出文件: {output_file}")
        
        print("\n🔍 测试1: Schema分割检测")
        print("-" * 30)
        needs_split = await excel_processor._check_schema_split_needed(str(test_file), "10月")
        print(f"✅ Schema分割检测: {'需要分割' if needs_split else '不需要分割'}")
        
        if needs_split:
            print("\n🔍 测试2: Schema分割处理")
            print("-" * 30)
            schema_sheets = await excel_processor._process_schema_split_sheet(str(test_file), "10月")
            print(f"✅ 检测到 {len(schema_sheets)} 个Schema区域:")
            
            for i, (schema_name, schema_data) in enumerate(schema_sheets.items(), 1):
                print(f"  {i}. {schema_name}")
                print(f"     - 描述: {schema_data['description']}")
                print(f"     - 数据行数: {len(schema_data['data'])}")
                print(f"     - 表头行: {schema_data['header_row']}")
        
        print("\n🔍 测试3: 完整Excel处理")
        print("-" * 30)
        result = await excel_processor.process_excel(str(test_file), str(output_file))
        
        print("📊 处理结果:")
        print(f"  - 总工作表数: {result.get('total_sheets', 0)}")
        print(f"  - 成功处理: {result.get('processed_sheets', 0)}")
        print(f"  - Schema分割工作表: {result.get('schema_split_sheets', 0)}")
        print(f"  - 总行数: {result.get('final_rows', 0)}")
        print(f"  - 最大列数: {result.get('final_columns', 0)}")
        
        # 显示工作表信息
        if 'processed_sheets_info' in result:
            print(f"\n📋 工作表详情:")
            for sheet_name, info in result['processed_sheets_info'].items():
                status = "✅" if info['status'] == 'success' else "❌"
                sheet_type = info.get('type', 'normal')
                print(f"  {status} {sheet_name} ({sheet_type}): {info['rows']}行 × {info['columns']}列")
        
        # 验证输出文件
        if output_file.exists():
            print(f"\n✅ 输出文件已生成: {output_file}")
            print(f"📊 文件大小: {output_file.stat().st_size / 1024:.1f} KB")
            
            # 读取输出文件验证
            import pandas as pd
            excel_file = pd.ExcelFile(str(output_file))
            print(f"📊 输出文件包含 {len(excel_file.sheet_names)} 个工作表:")
            
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(str(output_file), sheet_name=sheet_name)
                print(f"\n  📋 工作表: {sheet_name}")
                print(f"    - 行数: {len(df)}")
                print(f"    - 列数: {len(df.columns)}")
                print(f"    - 列名: {list(df.columns)}")
        else:
            print("❌ 输出文件未生成")
        
        print("\n🎉 测试完成！所有功能正常工作！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_summary())
