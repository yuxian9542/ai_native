# 快速启动指南

## 前置条件
- Python 3.9+
- Node.js 16+
- Elasticsearch 8.x
- OpenAI API Key

## 启动步骤

### 1. 启动Elasticsearch
```bash
docker run -d --name elasticsearch -p 9200:9200 -e "discovery.type=single-node" elasticsearch:8.11.0
```

### 2. 安装依赖
```bash
# 后端依赖
pip install -r backend/requirements.txt

# 前端依赖
cd frontend && npm install
```

### 3. 配置环境
```bash
cp env.template .env
# 编辑.env文件，填入OpenAI API Key
```

### 4. 启动服务
```bash
# 后端
cd backend && python main.py

# 前端
cd frontend && npm run dev
```

### 5. 访问系统
- 前端：http://localhost:5173
- 后端：http://localhost:8000

## 使用流程
1. 上传Excel文件
2. 输入分析问题
3. 查看分析结果
4. 管理文件列表