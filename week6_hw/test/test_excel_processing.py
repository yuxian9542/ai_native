#!/usr/bin/env python3
"""
Excel处理功能测试
测试Excel预处理、元数据生成和Elasticsearch索引
"""
import sys
import asyncio
import pandas as pd
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.services.excel_processor import excel_processor
from backend.services.metadata_generator import metadata_generator
from backend.utils.es_client import es_client


async def test_excel_processing():
    """测试Excel处理功能"""
    print("📊 Excel处理功能测试")
    print("=" * 50)
    
    # 1. 测试文件列表
    test_files = [
        "cola.xlsx",
        "复杂表头.xlsx", 
        "发电日志.xlsx"
    ]
    
    original_dir = PROJECT_ROOT / "data" / "original"
    processed_dir = PROJECT_ROOT / "data" / "processed"
    processed_dir.mkdir(exist_ok=True)
    
    for i, filename in enumerate(test_files, 1):
        print(f"\n{i}. 测试文件: {filename}")
        
        original_path = original_dir / filename
        if not original_path.exists():
            print(f"   ⚠️  文件不存在: {original_path}")
            continue
        
        try:
            # 处理Excel文件
            processed_filename = f"processed_{Path(filename).stem}.csv"
            processed_path = processed_dir / processed_filename
            
            print("   处理Excel文件...")
            log = await excel_processor.process_excel(
                str(original_path),
                str(processed_path)
            )
            
            print(f"   ✅ 处理完成:")
            print(f"     跳过行数: {log['skipped_rows']}")
            print(f"     表头行: {log['header_row']}")
            print(f"     合并单元格: {log['merged_cells_count']}")
            print(f"     最终行数: {log['final_rows']}")
            print(f"     最终列数: {log['final_columns']}")
            
            # 验证处理结果
            if processed_path.exists():
                df = pd.read_csv(processed_path)
                print(f"   📊 处理后数据: {len(df)} 行 x {len(df.columns)} 列")
                print(f"   📋 列名: {list(df.columns)}")
                
                # 显示前几行数据
                print("   📄 数据预览:")
                print(df.head(3).to_string())
                
                # 生成元数据
                print("   生成元数据...")
                metadata = await metadata_generator.generate_metadata(
                    filename,
                    str(original_path),
                    str(processed_path)
                )
                
                print(f"   ✅ 元数据生成成功:")
                print(f"     文件ID: {metadata.file_id}")
                print(f"     摘要: {metadata.summary}")
                print(f"     列数: {len(metadata.columns)}")
                print(f"     向量维度: {len(metadata.embedding) if metadata.embedding else 0}")
                
                # 显示列信息
                print("   📋 列信息:")
                for col in metadata.columns[:5]:  # 只显示前5列
                    print(f"     {col.name} ({col.type}): {col.description}")
                
                # 索引到Elasticsearch
                print("   索引到Elasticsearch...")
                doc = metadata.model_dump()
                doc["created_at"] = doc["created_at"].isoformat()
                doc["updated_at"] = doc["updated_at"].isoformat()
                
                await es_client.index_document(metadata.file_id, doc)
                print("   ✅ 已索引到Elasticsearch")
                
            else:
                print("   ❌ 处理后文件未生成")
                
        except Exception as e:
            print(f"   ❌ 处理失败: {e}")
            import traceback
            traceback.print_exc()
    
    # 2. 测试检索功能
    print(f"\n🔍 测试文件检索...")
    try:
        from backend.services.file_retriever import file_retriever
        
        test_queries = [
            "销售数据",
            "可乐",
            "发电",
            "复杂表头"
        ]
        
        for query in test_queries:
            print(f"   查询: '{query}'")
            results = await file_retriever.search_files(query, top_k=3)
            
            if results:
                print(f"   ✅ 找到 {len(results)} 个相关文件:")
                for result in results:
                    print(f"     - {result.file_name} (得分: {result.score:.2f})")
            else:
                print("   ℹ️  未找到相关文件")
                
    except Exception as e:
        print(f"   ❌ 检索测试失败: {e}")
    
    print("\n🎉 Excel处理功能测试完成！")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(test_excel_processing())
