#!/usr/bin/env python3
"""
快速测试Excel处理器
"""
import sys
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

async def quick_test():
    """快速测试"""
    print("🧪 快速测试Excel处理器")
    
    try:
        from backend.services.excel_processor import excel_processor
        print("✅ 成功导入excel_processor")
        
        # 测试Schema分割检测
        test_file = Path(__file__).parent.parent / "backend" / "data" / "original" / "复杂表头.xlsx"
        if test_file.exists():
            print("✅ 测试文件存在")
            
            # 测试Schema分割检测
            needs_split = await excel_processor._check_schema_split_needed(str(test_file), "10月")
            print(f"📊 Schema分割检测: {'需要分割' if needs_split else '不需要分割'}")
            
            if needs_split:
                schema_sheets = await excel_processor._process_schema_split_sheet(str(test_file), "10月")
                print(f"📋 检测到 {len(schema_sheets)} 个Schema区域")
                
                for schema_name, schema_data in schema_sheets.items():
                    print(f"  - {schema_name}: {len(schema_data['data'])}行")
        else:
            print("❌ 测试文件不存在")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(quick_test())