#!/usr/bin/env python3
"""
简化的Excel处理器测试
"""
import sys
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

async def test_excel_processor():
    """测试Excel处理器基本功能"""
    print("🧪 测试Excel处理器基本功能")
    
    from backend.services.excel_processor import excel_processor
    
    # 测试文件路径
    test_file = Path(__file__).parent.parent / "backend" / "data" / "original" / "复杂表头.xlsx"
    output_file = Path(__file__).parent / "data" / "processed" / "复杂表头_simple_test.xlsx"
    
    # 确保输出目录存在
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    if not test_file.exists():
        print(f"❌ 测试文件不存在: {test_file}")
        return
    
    try:
        print(f"📁 测试文件: {test_file}")
        print(f"📁 输出文件: {output_file}")
        
        # 处理Excel文件
        print("🔄 开始处理...")
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
        else:
            print("❌ 输出文件未生成")
            
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_excel_processor())
