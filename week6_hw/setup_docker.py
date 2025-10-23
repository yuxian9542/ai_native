#!/usr/bin/env python3
"""
Docker环境设置脚本
自动构建和配置Docker代码执行环境
"""
import subprocess
import sys
import time
from pathlib import Path


def run_command(cmd, check=True, capture_output=True):
    """运行命令"""
    print(f"🔧 执行: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True)
    
    if check and result.returncode != 0:
        print(f"❌ 命令执行失败: {result.stderr}")
        return False
    
    if capture_output and result.stdout:
        print(f"📝 输出: {result.stdout.strip()}")
    
    return True


def check_docker():
    """检查Docker是否安装"""
    print("🐳 检查Docker环境...")
    
    # 检查Docker是否安装
    if not run_command("docker --version", check=False):
        print("❌ Docker未安装，请先安装Docker Desktop")
        return False
    
    # 检查Docker是否运行
    if not run_command("docker info", check=False):
        print("❌ Docker未运行，请启动Docker Desktop")
        return False
    
    print("✅ Docker环境正常")
    return True


def build_image():
    """构建Docker镜像"""
    print("\n🔨 构建代码执行镜像...")
    
    docker_dir = Path(__file__).parent / "docker"
    dockerfile = docker_dir / "Dockerfile.code-executor"
    
    if not dockerfile.exists():
        print("❌ Dockerfile不存在")
        return False
    
    cmd = f"docker build -f {dockerfile} -t excel-analysis-code-executor {docker_dir}"
    if run_command(cmd):
        print("✅ 镜像构建成功")
        return True
    else:
        print("❌ 镜像构建失败")
        return False


def create_container():
    """创建Docker容器"""
    print("\n🚀 创建代码执行容器...")
    
    # 停止并删除现有容器
    run_command("docker stop excel-analysis-code-executor", check=False)
    run_command("docker rm excel-analysis-code-executor", check=False)
    
    # 创建新容器
    data_dir = Path(__file__).parent / "data" / "processed"
    backend_dir = Path(__file__).parent / "backend"
    
    cmd = f"""
    docker run -d \
        --name excel-analysis-code-executor \
        -v "{data_dir}:/app/data:ro" \
        -v "{backend_dir}:/app/backend:ro" \
        -w /app/workspace \
        excel-analysis-code-executor \
        tail -f /dev/null
    """
    
    if run_command(cmd):
        print("✅ 容器创建成功")
        return True
    else:
        print("❌ 容器创建失败")
        return False


def test_container():
    """测试容器功能"""
    print("\n🧪 测试容器功能...")
    
    test_code = '''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

print("=== 环境测试 ===")
print(f"Python版本: {sys.version}")
print(f"pandas版本: {pd.__version__}")
print(f"numpy版本: {np.__version__}")

# 创建测试数据
data = {"x": [1, 2, 3, 4, 5], "y": [2, 4, 6, 8, 10]}
df = pd.DataFrame(data)
print("\\n=== 数据测试 ===")
print(df)

# 创建测试图表
plt.figure(figsize=(8, 6))
plt.plot(df["x"], df["y"], "o-", linewidth=2, markersize=8)
plt.title("Docker环境测试图表")
plt.xlabel("X轴")
plt.ylabel("Y轴")
plt.grid(True, alpha=0.3)
plt.savefig("/app/workspace/test_output.png", dpi=300, bbox_inches='tight')
print("\\n=== 图表测试 ===")
print("图表已生成并保存")

print("\\n✅ 所有测试通过！")
'''
    
    cmd = f'docker exec excel-analysis-code-executor python -c "{test_code}"'
    if run_command(cmd, capture_output=False):
        print("✅ 容器测试通过")
        return True
    else:
        print("❌ 容器测试失败")
        return False


def show_status():
    """显示容器状态"""
    print("\n📊 容器状态:")
    run_command("docker ps -a --filter name=excel-analysis-code-executor", capture_output=False)


def main():
    """主函数"""
    print("🚀 Excel智能分析系统 - Docker环境设置")
    print("=" * 50)
    
    # 1. 检查Docker环境
    if not check_docker():
        sys.exit(1)
    
    # 2. 构建镜像
    if not build_image():
        sys.exit(1)
    
    # 3. 创建容器
    if not create_container():
        sys.exit(1)
    
    # 4. 等待容器启动
    print("\n⏳ 等待容器启动...")
    time.sleep(3)
    
    # 5. 测试容器
    if not test_container():
        print("❌ 容器测试失败，但容器已创建")
        print("可以手动运行测试: python test/test_docker_execution.py")
    else:
        print("🎉 Docker环境设置完成！")
    
    # 6. 显示状态
    show_status()
    
    print("\n📝 使用说明:")
    print("1. 启动后端服务: python -c \"from backend.main import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8000)\"")
    print("2. 运行Docker测试: python test/test_docker_execution.py")
    print("3. 停止容器: docker stop excel-analysis-code-executor")
    print("4. 删除容器: docker rm excel-analysis-code-executor")


if __name__ == "__main__":
    main()
