#!/usr/bin/env python3
"""
Docker容器管理脚本
用于构建、启动、停止代码执行环境
"""
import subprocess
import sys
import time
from pathlib import Path


def run_command(cmd, check=True):
    """运行命令"""
    print(f"执行命令: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if check and result.returncode != 0:
        print(f"命令执行失败: {result.stderr}")
        sys.exit(1)
    
    return result


def build_image():
    """构建Docker镜像"""
    print("🔨 构建代码执行环境镜像...")
    
    dockerfile_path = Path(__file__).parent / "Dockerfile.code-executor"
    if not dockerfile_path.exists():
        print("❌ Dockerfile不存在")
        return False
    
    cmd = f"docker build -f {dockerfile_path} -t excel-analysis-code-executor {dockerfile_path.parent}"
    result = run_command(cmd)
    
    print("✅ 镜像构建完成")
    return True


def start_container():
    """启动容器"""
    print("🚀 启动代码执行容器...")
    
    # 检查容器是否已存在
    result = run_command("docker ps -a --filter name=excel-analysis-code-executor --format '{{.Names}}'", check=False)
    
    if "excel-analysis-code-executor" in result.stdout:
        # 容器已存在，启动它
        run_command("docker start excel-analysis-code-executor")
        print("✅ 容器已启动")
    else:
        # 创建新容器
        cmd = """
        docker run -d \
            --name excel-analysis-code-executor \
            -v "{}:/app/data:ro" \
            -v "{}:/app/backend:ro" \
            -w /app/workspace \
            excel-analysis-code-executor \
            tail -f /dev/null
        """.format(
            str(Path(__file__).parent.parent / "data" / "processed"),
            str(Path(__file__).parent.parent / "backend")
        )
        
        run_command(cmd)
        print("✅ 容器创建并启动完成")


def stop_container():
    """停止容器"""
    print("🛑 停止代码执行容器...")
    
    run_command("docker stop excel-analysis-code-executor", check=False)
    print("✅ 容器已停止")


def remove_container():
    """删除容器"""
    print("🗑️ 删除代码执行容器...")
    
    run_command("docker rm excel-analysis-code-executor", check=False)
    print("✅ 容器已删除")


def test_container():
    """测试容器"""
    print("🧪 测试代码执行容器...")
    
    test_code = '''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

print("测试开始...")
print(f"pandas版本: {pd.__version__}")
print(f"numpy版本: {np.__version__}")

# 创建测试数据
data = {"x": [1, 2, 3, 4, 5], "y": [2, 4, 6, 8, 10]}
df = pd.DataFrame(data)
print("数据框:")
print(df)

# 创建简单图表
plt.figure(figsize=(8, 6))
plt.plot(df["x"], df["y"], "o-")
plt.title("测试图表")
plt.xlabel("X轴")
plt.ylabel("Y轴")
plt.savefig("/app/workspace/test_output.png")
print("图表已保存")

print("测试完成!")
'''
    
    cmd = f'docker exec excel-analysis-code-executor python -c "{test_code}"'
    result = run_command(cmd)
    
    if result.returncode == 0:
        print("✅ 容器测试通过")
        print("输出:")
        print(result.stdout)
    else:
        print("❌ 容器测试失败")
        print("错误:")
        print(result.stderr)


def show_status():
    """显示容器状态"""
    print("📊 容器状态:")
    
    result = run_command("docker ps -a --filter name=excel-analysis-code-executor", check=False)
    print(result.stdout)
    
    if "excel-analysis-code-executor" in result.stdout:
        print("\n📋 容器详细信息:")
        result = run_command("docker inspect excel-analysis-code-executor", check=False)
        print(result.stdout)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python manage_docker.py <command>")
        print("命令:")
        print("  build    - 构建Docker镜像")
        print("  start    - 启动容器")
        print("  stop     - 停止容器")
        print("  restart  - 重启容器")
        print("  remove   - 删除容器")
        print("  test     - 测试容器")
        print("  status   - 显示状态")
        print("  setup    - 完整设置（构建+启动+测试）")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "build":
        build_image()
    elif command == "start":
        start_container()
    elif command == "stop":
        stop_container()
    elif command == "restart":
        stop_container()
        time.sleep(2)
        start_container()
    elif command == "remove":
        stop_container()
        remove_container()
    elif command == "test":
        test_container()
    elif command == "status":
        show_status()
    elif command == "setup":
        print("🔧 开始完整设置...")
        build_image()
        start_container()
        time.sleep(3)
        test_container()
        print("🎉 设置完成！")
    else:
        print(f"未知命令: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
