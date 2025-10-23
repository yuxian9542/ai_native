#!/usr/bin/env python3
"""
测试Excel文件上传功能
"""
import requests
import json
from pathlib import Path

def test_upload():
    """测试文件上传"""
    # 使用现有的测试文件
    test_file = Path("data/original/cola.xlsx")
    
    if not test_file.exists():
        print("❌ 测试文件不存在:", test_file)
        return
    
    print("🚀 开始测试Excel文件上传...")
    print(f"📁 测试文件: {test_file}")
    
    # 上传文件
    with open(test_file, 'rb') as f:
        files = {'file': (test_file.name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        
        try:
            response = requests.post(
                'http://localhost:8000/api/files/upload',
                files=files,
                timeout=60
            )
            
            print(f"📊 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 上传成功!")
                print(f"📄 文件ID: {result.get('file_id')}")
                print(f"📄 文件名: {result.get('file_name')}")
                print(f"💬 消息: {result.get('message')}")
                
                # 测试获取文件列表
                print("\n🔍 测试获取文件列表...")
                list_response = requests.get('http://localhost:8000/api/files')
                if list_response.status_code == 200:
                    files_data = list_response.json()
                    print(f"📋 文件列表: {len(files_data.get('files', []))} 个文件")
                    for file_info in files_data.get('files', []):
                        print(f"  - {file_info.get('file_name')} (ID: {file_info.get('file_id')})")
                else:
                    print("❌ 获取文件列表失败")
                    
            else:
                print("❌ 上传失败!")
                print(f"错误信息: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求失败: {e}")
        except Exception as e:
            print(f"❌ 处理失败: {e}")

def test_health():
    """测试健康检查"""
    print("🏥 测试健康检查...")
    try:
        response = requests.get('http://localhost:8000/api/health')
        if response.status_code == 200:
            health_data = response.json()
            print("✅ 服务健康!")
            print(f"📊 状态: {health_data.get('status')}")
            print(f"🔍 Elasticsearch: {health_data.get('elasticsearch')}")
            print(f"🤖 OpenAI: {health_data.get('openai')}")
        else:
            print("❌ 健康检查失败")
    except Exception as e:
        print(f"❌ 健康检查请求失败: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("Excel智能分析系统 - 上传测试")
    print("=" * 50)
    
    # 测试健康检查
    test_health()
    print()
    
    # 测试文件上传
    test_upload()
    
    print("\n" + "=" * 50)
    print("测试完成!")
    print("=" * 50)

