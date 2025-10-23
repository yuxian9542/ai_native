# 🐳 Docker代码执行系统指南

## 概述

Excel智能分析系统现在支持在Docker容器中执行Python代码，提供更好的隔离性、一致性和安全性。

## 🏗️ 架构设计

### 执行环境
- **基础镜像**: `python:3.11-slim`
- **预装包**: pandas, numpy, matplotlib, openpyxl, seaborn, plotly, scipy, scikit-learn
- **安全措施**: 非root用户执行，只读数据访问
- **超时控制**: 60秒执行超时

### 文件结构
```
week6_hw/
├── docker/
│   ├── Dockerfile.code-executor    # 代码执行环境镜像
│   ├── docker-compose.yml          # 容器编排配置
│   └── manage_docker.py            # 容器管理脚本
├── backend/services/
│   ├── code_executor.py            # 本地代码执行器
│   ├── docker_code_executor.py     # Docker代码执行器
│   └── unified_code_executor.py    # 统一执行器
└── test/
    └── test_docker_execution.py    # Docker执行测试
```

## 🚀 快速开始

### 1. 自动设置
```bash
cd week6_hw
python setup_docker.py
```

### 2. 手动设置
```bash
# 构建镜像
cd week6_hw/docker
docker build -f Dockerfile.code-executor -t excel-analysis-code-executor .

# 创建并启动容器
docker run -d \
    --name excel-analysis-code-executor \
    -v "$(pwd)/../data/processed:/app/data:ro" \
    -v "$(pwd)/../backend:/app/backend:ro" \
    -w /app/workspace \
    excel-analysis-code-executor \
    tail -f /dev/null
```

### 3. 测试执行
```bash
python test/test_docker_execution.py
```

## 🔧 配置选项

### 环境变量
在 `.env` 文件中配置：
```env
# 代码执行配置
USE_DOCKER_EXECUTION=true
CODE_EXECUTION_TIMEOUT=60
```

### 代码执行器选择
系统会根据配置自动选择执行器：
- `USE_DOCKER_EXECUTION=true`: 使用Docker执行
- `USE_DOCKER_EXECUTION=false`: 使用本地执行

## 📊 功能特性

### 1. 安全执行
- **代码检查**: 阻止危险操作（文件写入、系统调用等）
- **容器隔离**: 在独立容器中执行，不影响主机
- **资源限制**: 60秒超时，防止无限循环
- **只读访问**: 数据文件只读挂载

### 2. 丰富的库支持
```python
# 预装的数据分析库
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
from sklearn import datasets
```

### 3. 图表生成
- **matplotlib**: 静态图表
- **seaborn**: 统计图表
- **plotly**: 交互式图表
- **中文字体支持**: 自动配置中文字体

## 🛠️ 管理命令

### 使用管理脚本
```bash
cd week6_hw/docker
python manage_docker.py <command>
```

**可用命令**:
- `build`: 构建Docker镜像
- `start`: 启动容器
- `stop`: 停止容器
- `restart`: 重启容器
- `remove`: 删除容器
- `test`: 测试容器
- `status`: 显示状态
- `setup`: 完整设置

### 直接Docker命令
```bash
# 查看容器状态
docker ps -a --filter name=excel-analysis-code-executor

# 查看容器日志
docker logs excel-analysis-code-executor

# 进入容器
docker exec -it excel-analysis-code-executor bash

# 停止容器
docker stop excel-analysis-code-executor

# 删除容器
docker rm excel-analysis-code-executor
```

## 🧪 测试验证

### 1. 基础功能测试
```bash
python test/test_docker_execution.py
```

### 2. 完整系统测试
```bash
python test/run_all_tests.py
```

### 3. 手动测试
```bash
# 在容器中执行简单代码
docker exec excel-analysis-code-executor python -c "
import pandas as pd
import matplotlib.pyplot as plt
print('Docker环境正常')
"
```

## 🔍 故障排除

### 常见问题

#### 1. Docker未安装
```
❌ Docker未安装，请先安装Docker Desktop
```
**解决**: 安装Docker Desktop并启动服务

#### 2. 镜像构建失败
```
❌ 镜像构建失败
```
**解决**: 检查网络连接，确保能访问Docker Hub

#### 3. 容器启动失败
```
❌ 容器创建失败
```
**解决**: 检查端口占用，确保Docker服务运行正常

#### 4. 代码执行超时
```
❌ 代码执行超时（超过60秒）
```
**解决**: 优化代码性能，或增加超时时间

#### 5. 权限问题
```
❌ 权限被拒绝
```
**解决**: 确保Docker有足够权限访问数据目录

### 调试步骤

1. **检查Docker状态**
   ```bash
   docker info
   ```

2. **查看容器日志**
   ```bash
   docker logs excel-analysis-code-executor
   ```

3. **进入容器调试**
   ```bash
   docker exec -it excel-analysis-code-executor bash
   ```

4. **检查挂载目录**
   ```bash
   docker exec excel-analysis-code-executor ls -la /app/data
   ```

## 📈 性能优化

### 1. 容器预热
```python
# 在应用启动时预热容器
await docker_code_executor._get_or_create_container()
```

### 2. 资源限制
```yaml
# 在docker-compose.yml中添加资源限制
deploy:
  resources:
    limits:
      memory: 1G
      cpus: '0.5'
```

### 3. 缓存优化
- 容器保持运行状态，避免重复创建
- 预加载常用库，减少启动时间

## 🔒 安全考虑

### 1. 代码沙箱
- 禁止文件写入操作
- 禁止系统调用
- 禁止网络访问

### 2. 资源限制
- 执行时间限制
- 内存使用限制
- CPU使用限制

### 3. 数据隔离
- 只读数据访问
- 临时工作目录
- 自动清理机制

## 🚀 部署建议

### 开发环境
- 使用Docker Desktop
- 本地数据目录挂载
- 快速迭代测试

### 生产环境
- 使用Docker Swarm或Kubernetes
- 持久化存储
- 监控和日志收集

## 📝 最佳实践

### 1. 代码编写
```python
# 好的实践
import pandas as pd
df = pd.read_csv(CSV_FILE_PATH)
result = df.groupby('category').sum()
plt.savefig(OUTPUT_IMAGE_PATH)

# 避免的做法
import os  # 禁止
import subprocess  # 禁止
open('file.txt', 'w')  # 禁止写入
```

### 2. 错误处理
```python
try:
    # 数据分析代码
    result = analyze_data()
    print("分析完成")
except Exception as e:
    print(f"分析失败: {e}")
```

### 3. 资源管理
- 及时释放大对象
- 避免无限循环
- 合理使用内存

---

**Docker代码执行系统已准备就绪！** 🎉

通过Docker容器执行代码，系统现在具备了更好的隔离性、一致性和安全性，能够为用户提供稳定可靠的数据分析服务。
