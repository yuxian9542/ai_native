#!/usr/bin/env python3
"""
运行所有测试的主脚本
"""
import sys
import asyncio
import subprocess
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def run_test_script(script_name, description):
    """运行测试脚本"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([
            sys.executable, 
            str(PROJECT_ROOT / "test" / script_name)
        ], capture_output=True, text=True, timeout=300)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"❌ 测试超时: {script_name}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def check_backend_running():
    """检查后端是否运行"""
    import requests
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def main():
    """主函数"""
    print("🚀 Excel智能分析系统 - 完整测试套件")
    print("=" * 60)
    
    # 检查后端服务
    print("1. 检查后端服务状态...")
    if not check_backend_running():
        print("❌ 后端服务未运行！")
        print("请先启动后端服务:")
        print("cd week6_hw")
        print("python -c \"from backend.main import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8000)\"")
        return
    else:
        print("✅ 后端服务运行正常")
    
    # 运行测试
    tests = [
        ("quick_test.py", "快速功能测试"),
        ("test_excel_processing.py", "Excel处理功能测试"),
        ("test_code_execution.py", "代码生成和执行测试"),
        ("test_backend.py", "完整后端功能测试")
    ]
    
    results = {}
    
    for script, description in tests:
        success = run_test_script(script, description)
        results[description] = "✅ 通过" if success else "❌ 失败"
    
    # 输出测试结果汇总
    print(f"\n{'='*60}")
    print("📊 测试结果汇总")
    print(f"{'='*60}")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        print(f"{test_name:30} : {result}")
        if "✅" in result:
            passed += 1
    
    print("-" * 60)
    print(f"总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统功能完整！")
    else:
        print("⚠️  部分测试失败，请检查相关功能")
    
    print("=" * 60)


if __name__ == "__main__":
    main()

