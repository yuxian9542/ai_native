#!/usr/bin/env python3
"""
简单的虚拟环境测试
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.services.virtualenv_code_executor import virtualenv_code_executor

def test_simple():
    """简单测试"""
    print("🐍 简单虚拟环境测试")
    print("=" * 30)
    
    # 测试环境
    print("1. 测试环境...")
    if virtualenv_code_executor.test_environment():
        print("   ✅ 环境正常")
    else:
        print("   ❌ 环境异常")
        return
    
    print("2. 测试Python路径...")
    print(f"   Python可执行文件: {virtualenv_code_executor.python_executable}")
    
    print("3. 测试工作目录...")
    print(f"   工作目录: {virtualenv_code_executor.work_dir}")
    
    print("\n✅ 简单测试完成！")

if __name__ == "__main__":
    test_simple()

