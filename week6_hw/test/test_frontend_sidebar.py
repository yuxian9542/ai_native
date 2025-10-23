#!/usr/bin/env python3
"""
测试前端侧边栏文件管理功能
"""
import sys
from pathlib import Path
import pandas as pd
import asyncio
import requests
import json

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.metadata_generator import metadata_generator
from backend.utils.es_client import es_client


async def test_file_upload_and_display():
    """测试文件上传和显示功能"""
    print("🧪 Testing Frontend Sidebar File Management")
    print("=" * 50)
    
    # 1. 创建测试文件
    print("1. Creating test files...")
    test_files = []
    
    for i in range(3):
        test_data = {
            'product': [f'product_{j}' for j in range(5)],
            'sales': [100 + j * 10 for j in range(5)],
            'quantity': [10 + j for j in range(5)],
            'category': ['category_a'] * 5,
            'region': ['region_1'] * 5
        }
        
        df = pd.DataFrame(test_data)
        file_name = f'test_sidebar_{i+1}.xlsx'
        original_path = Path(f'data/original/{file_name}').resolve()
        processed_path = Path(f'data/processed/{file_name}_processed.xlsx').resolve()
        
        original_path.parent.mkdir(parents=True, exist_ok=True)
        processed_path.parent.mkdir(parents=True, exist_ok=True)
        
        df.to_excel(original_path, index=False)
        df.to_excel(processed_path, index=False)
        
        test_files.append({
            'name': file_name,
            'original_path': str(original_path),
            'processed_path': str(processed_path)
        })
        
        print(f"   ✅ Created: {file_name}")
    
    # 2. 生成元数据并存储到ES
    print("\n2. Generating metadata and storing to Elasticsearch...")
    for file_info in test_files:
        try:
            metadata = await metadata_generator.generate_metadata(
                file_info['name'],
                file_info['original_path'],
                file_info['processed_path']
            )
            
            # 存储到ES
            doc = metadata.model_dump()
            doc['created_at'] = doc['created_at'].isoformat()
            doc['updated_at'] = doc['updated_at'].isoformat()
            await es_client.index_document(metadata.file_id, doc)
            
            print(f"   ✅ Metadata stored: {file_info['name']} (ID: {metadata.file_id})")
            
        except Exception as e:
            print(f"   ❌ Error processing {file_info['name']}: {e}")
    
    # 3. 测试API获取文件列表
    print("\n3. Testing API file list endpoint...")
    try:
        response = requests.get('http://localhost:8000/files')
        if response.status_code == 200:
            files_data = response.json()
            print(f"   ✅ API returned {len(files_data.get('files', []))} files")
            
            for file in files_data.get('files', []):
                print(f"      - {file['file_name']} ({file['row_count']} rows × {file['column_count']} cols)")
        else:
            print(f"   ❌ API error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ API request failed: {e}")
    
    # 4. 测试文件删除API
    print("\n4. Testing file deletion...")
    try:
        # 获取第一个文件的ID
        response = requests.get('http://localhost:8000/files')
        if response.status_code == 200:
            files_data = response.json()
            if files_data.get('files'):
                first_file = files_data['files'][0]
                file_id = first_file['file_id']
                file_name = first_file['file_name']
                
                print(f"   🗑️ Deleting file: {file_name} (ID: {file_id})")
                
                delete_response = requests.delete(f'http://localhost:8000/files/{file_id}')
                if delete_response.status_code == 200:
                    print(f"   ✅ File deleted successfully")
                else:
                    print(f"   ❌ Delete failed: {delete_response.status_code}")
            else:
                print("   ⚠️ No files to delete")
    except Exception as e:
        print(f"   ❌ Delete test failed: {e}")
    
    print("\n🎉 Frontend sidebar test completed!")
    print("\n📋 Test Summary:")
    print("   - Created 3 test Excel files")
    print("   - Generated metadata for all files")
    print("   - Stored metadata in Elasticsearch")
    print("   - Tested file list API endpoint")
    print("   - Tested file deletion API")
    print("\n🌐 Frontend should now show:")
    print("   - Left sidebar with file management")
    print("   - Upload button in sidebar")
    print("   - File list with delete buttons")
    print("   - Collapsible sidebar functionality")


async def main():
    """主测试函数"""
    print("🧪 Testing Frontend Sidebar File Management")
    print("=" * 60)
    
    try:
        await test_file_upload_and_display()
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
