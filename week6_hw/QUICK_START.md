# 快速启动指南

本指南帮助您在5分钟内启动Excel智能分析系统。

## 前置条件检查

✅ Python 3.9+ 已安装  
✅ Node.js 16+ 已安装  
✅ Docker 已安装并运行  
✅ OpenAI API Key 已获取

## 启动步骤

### 1. 启动Elasticsearch（2分钟）

```bash
docker run -d \
  --name elasticsearch \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:8.10.0
```

等待30秒后验证：
```bash
curl http://localhost:9200
```

### 2. 配置后端（1分钟）

```bash
# 激活虚拟环境
.ai_native\Scripts\Activate.ps1

# 进入backend目录
cd week6_hw/backend

# 安装依赖
pip install -r requirements.txt
```

创建 `week6_hw/.env` 文件：
```env
OPENAI_API_KEY=sk-your-api-key-here
ELASTICSEARCH_URL=http://localhost:9200
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
UPLOAD_DIR=./data/original
PROCESSED_DIR=./data/processed
OUTPUT_DIR=./data/output
CODE_EXECUTION_TIMEOUT=60
MAX_FILE_SIZE=52428800
```

### 3. 初始化Elasticsearch索引（30秒）

```bash
python scripts/init_es_index.py
```

### 4. 启动后端（30秒）

```bash
python main.py
```

看到以下输出表示成功：
```
==================================================
Excel智能分析系统启动中...
后端服务: http://0.0.0.0:8000
API文档: http://0.0.0.0:8000/docs
Elasticsearch: http://localhost:9200
==================================================
✓ Elasticsearch连接成功
```

### 5. 启动前端（1分钟）

打开新终端：

```bash
cd week6_hw/frontend

# 安装依赖（首次）
npm install

# 启动
npm run dev
```

## 验证安装

1. 打开浏览器访问 http://localhost:3000
2. 看到"Excel智能分析系统"界面
3. 右上角显示"已连接"状态（绿色）

## 第一次使用

### 上传测试数据

系统已包含测试Excel文件在 `data/original/` 目录。使用Python上传：

```python
import requests

with open('data/original/cola.xlsx', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/files/upload',
        files={'file': f}
    )
    print(response.json())
```

### 测试问题

在Web界面输入：
- "这个文件包含什么数据？"
- "统计一下数据"
- "画个图表"

## 常见问题

### Q: Elasticsearch启动失败
A: 检查Docker是否运行，端口9200是否被占用

### Q: 后端连接ES失败
A: 等待ES完全启动（约30秒），再启动后端

### Q: 前端显示"未连接"
A: 确保后端已启动在8000端口，刷新页面

### Q: OpenAI API调用失败
A: 检查.env中的API Key是否正确，是否有网络访问限制

## 下一步

- 阅读完整的 [README.md](README.md) 了解更多功能
- 查看 [API文档](http://localhost:8000/docs)
- 上传自己的Excel文件开始分析

## 停止服务

```bash
# 停止后端：Ctrl+C
# 停止前端：Ctrl+C

# 停止Elasticsearch
docker stop elasticsearch

# 删除Elasticsearch容器（可选）
docker rm elasticsearch
```

享受使用！ 🎉

