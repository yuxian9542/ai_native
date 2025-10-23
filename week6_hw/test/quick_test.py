#!/usr/bin/env python3
"""
快速测试脚本 - 验证核心功能
"""
import sys
import asyncio
import requests
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

async def quick_test():
    """快速测试核心功能"""
    print("🚀 Excel智能分析系统 - 快速测试")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # 1. 检查后端服务
    print("1. 检查后端服务...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ 后端服务运行正常")
        else:
            print("   ❌ 后端服务异常")
            return
    except Exception as e:
        print(f"   ❌ 无法连接到后端: {e}")
        return
    
    # 2. 测试文件上传
    print("2. 测试文件上传...")
    test_file = PROJECT_ROOT / "data" / "original" / "cola.xlsx"
    
    if not test_file.exists():
        print("   ❌ 测试文件不存在")
        return
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': (test_file.name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            response = requests.post(f"{base_url}/api/files/upload", files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"   ✅ 文件上传成功: {result.get('file_name')}")
                file_id = result.get('file_id')
            else:
                print(f"   ❌ 文件上传失败: {result.get('error')}")
                return
        else:
            print(f"   ❌ 文件上传失败: HTTP {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ 文件上传异常: {e}")
        return
    
    # 3. 测试文件列表
    print("3. 测试文件列表...")
    try:
        response = requests.get(f"{base_url}/api/files", timeout=10)
        if response.status_code == 200:
            files_data = response.json()
            file_count = len(files_data.get('files', []))
            print(f"   ✅ 文件列表获取成功: {file_count} 个文件")
        else:
            print("   ❌ 文件列表获取失败")
    except Exception as e:
        print(f"   ❌ 文件列表获取异常: {e}")
    
    # 4. 测试文件详情
    print("4. 测试文件详情...")
    try:
        response = requests.get(f"{base_url}/api/files/{file_id}", timeout=10)
        if response.status_code == 200:
            file_detail = response.json()
            print(f"   ✅ 文件详情获取成功: {file_detail.get('file_name')}")
        else:
            print("   ❌ 文件详情获取失败")
    except Exception as e:
        print(f"   ❌ 文件详情获取异常: {e}")
    
    print("\n🎉 快速测试完成！")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(quick_test())
