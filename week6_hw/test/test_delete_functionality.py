#!/usr/bin/env python3
"""
测试文件删除功能
验证文件删除API - 只删除处理后的文件，保留原始文件
"""
import sys
from pathlib import Path
import pandas as pd
import asyncio
import requests
import json

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.excel_processor import ExcelProcessor
from backend.services.metadata_generator import MetadataGenerator
from backend.utils.es_client import es_client


async def test_delete_functionality():
    """测试文件删除功能"""
    print("🗑️ Testing File Delete Functionality")
    print("=" * 50)
    
    # 1. 创建测试文件
    print("1. Creating test files...")
    test_data = {
        'product': ['cola', 'sprite', 'fanta'],
        'sales': [100, 150, 90],
        'quantity': [10, 15, 9],
        'month': ['Jan', 'Jan', 'Jan']
    }
    
    # 创建原始Excel文件
    original_path = Path("data/original/test_delete.xlsx").resolve()
    original_path.parent.mkdir(parents=True, exist_ok=True)
    
    df = pd.DataFrame(test_data)
    df.to_excel(original_path, index=False)
    print(f"   ✅ Original file created: {original_path}")
    
    # 2. 处理Excel文件
    print("2. Processing Excel file...")
    processor = ExcelProcessor()
    processed_path = Path("data/processed/test_delete_processed.xlsx").resolve()
    
    try:
        log = await processor.process_excel(str(original_path), str(processed_path))
        print(f"   ✅ Excel processed successfully")
        
        # 验证处理后的文件存在
        if not processed_path.exists():
            print("   ❌ Processed file not found")
            return False
            
    except Exception as e:
        print(f"   ❌ Excel processing failed: {e}")
        return False
    
    # 3. 生成元数据并存储到ES
    print("3. Generating metadata and storing in ES...")
    metadata_gen = MetadataGenerator()
    
    try:
        metadata = await metadata_gen.generate_metadata(
            "test_delete.xlsx",
            str(original_path),
            str(processed_path)
        )
        print(f"   ✅ Metadata generated successfully")
        print(f"   📁 File ID: {metadata.file_id}")
        
        # 存储到ES
        doc = metadata.model_dump()
        doc["created_at"] = doc["created_at"].isoformat()
        doc["updated_at"] = doc["updated_at"].isoformat()
        
        await es_client.index_document(metadata.file_id, doc)
        print(f"   ✅ Document stored in ES")
        
        # 验证文件在ES中存在
        stored_doc = await es_client.get_document(metadata.file_id)
        if not stored_doc:
            print("   ❌ Document not found in ES")
            return False
        print(f"   ✅ Document verified in ES")
        
    except Exception as e:
        print(f"   ❌ Metadata generation/storage failed: {e}")
        return False
    
    # 4. 测试删除API
    print("4. Testing delete API...")
    try:
        # 调用删除API
        response = requests.delete(f"http://localhost:8000/api/files/{metadata.file_id}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Delete API successful: {result.get('message', '')}")
        else:
            print(f"   ❌ Delete API failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Delete API error: {e}")
        return False
    
    # 5. 验证文件删除状态
    print("5. Verifying file deletion status...")
    
    # 检查原始文件（应该保留）
    if original_path.exists():
        print(f"   ✅ Original file preserved: {original_path}")
    else:
        print(f"   ❌ Original file was deleted (should be preserved): {original_path}")
        return False
    
    # 检查处理后的文件（应该被删除）
    if processed_path.exists():
        print(f"   ❌ Processed file still exists: {processed_path}")
        return False
    else:
        print(f"   ✅ Processed file deleted: {processed_path}")
    
    # 检查ES文档
    try:
        stored_doc = await es_client.get_document(metadata.file_id)
        if stored_doc:
            print(f"   ❌ Document still exists in ES")
            return False
        else:
            print(f"   ✅ Document deleted from ES")
    except Exception as e:
        # 文档不存在时会抛出异常，这是正常的
        print(f"   ✅ Document deleted from ES (not found)")
    
    # 6. 测试删除不存在的文件
    print("6. Testing delete non-existent file...")
    try:
        fake_id = "fake-file-id-12345"
        response = requests.delete(f"http://localhost:8000/api/files/{fake_id}")
        
        if response.status_code == 404:
            print(f"   ✅ Correctly returned 404 for non-existent file")
        else:
            print(f"   ❌ Expected 404, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing non-existent file: {e}")
        return False
    
    print("\\n🎉 File delete functionality test completed successfully!")
    return True


async def test_backend_imports():
    """测试后端导入"""
    print("🔧 Testing backend imports...")
    try:
        from backend.api.rest import router
        from backend.utils.es_client import es_client
        print("   ✅ Backend imports successful")
        return True
    except Exception as e:
        print(f"   ❌ Backend import failed: {e}")
        return False


if __name__ == "__main__":
    print("Starting delete functionality tests...")
    
    # 测试后端导入
    import_success = asyncio.run(test_backend_imports())
    if not import_success:
        print("\\n❌ Backend import test failed!")
        sys.exit(1)
    
    # 测试删除功能
    success = asyncio.run(test_delete_functionality())
    if success:
        print("\\n✅ All delete functionality tests passed!")
    else:
        print("\\n❌ Some delete functionality tests failed!")
        sys.exit(1)
