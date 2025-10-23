# Excel智能分析系统

基于AI的Excel数据分析平台，支持自然语言查询、智能文件检索、自动代码生成和安全执行。

## 🎯 核心功能

- ✅ **智能Excel预处理**：自动识别无关行、处理多级表头、拆分合并单元格
- ✅ **语义检索**：使用Elasticsearch混合检索（BM25 + 向量相似度）快速找到相关数据
- ✅ **AI代码生成**：GPT-4根据问题自动生成Python分析代码
- ✅ **安全执行**：隔离环境执行代码，支持数据分析和可视化
- ✅ **实时通信**：WebSocket实时推送分析进度
- ✅ **语音输入**：支持语音提问，提升交互体验
- ✅ **数据溯源**：完整展示使用的文件、列和分析逻辑

## 📁 项目结构

```
week6_hw/
├── backend/                    # 后端目录
│   ├── main.py                # FastAPI主应用
│   ├── config.py              # 配置管理
│   ├── models/                # 数据模型
│   │   ├── schemas.py         # Pydantic模型
│   │   └── elasticsearch.py   # ES索引定义
│   ├── services/              # 业务逻辑
│   │   ├── excel_processor.py      # Excel预处理
│   │   ├── metadata_generator.py   # 元数据生成
│   │   ├── file_retriever.py       # 文件检索
│   │   ├── code_generator.py       # 代码生成
│   │   └── code_executor.py        # 代码执行
│   ├── api/                   # API层
│   │   ├── rest.py           # REST API
│   │   └── websocket.py      # WebSocket
│   ├── utils/                 # 工具类
│   │   ├── openai_client.py  # OpenAI封装
│   │   └── es_client.py      # ES客户端
│   ├── scripts/               # 脚本
│   │   └── init_es_index.py  # 初始化ES索引
│   └── requirements.txt       # Python依赖
│
├── frontend/                   # 前端目录
│   ├── src/
│   │   ├── App.jsx           # 主应用组件
│   │   ├── App.css           # 样式
│   │   ├── main.jsx          # 入口
│   │   └── index.css         # 全局样式
│   ├── index.html            # HTML模板
│   ├── package.json          # 前端依赖
│   └── vite.config.js        # Vite配置
│
├── data/                      # 数据目录
│   ├── original/             # 原始Excel文件
│   ├── processed/            # 处理后CSV文件
│   └── output/               # 生成的图表
│
└── README.md                 # 项目文档
```

## 🚀 快速开始

### 1. 环境准备

**必需软件：**
- Python 3.9+
- Node.js 16+
- Elasticsearch 8.x
- OpenAI API Key

### 2. 启动Elasticsearch

**使用Docker（推荐）：**

```bash
docker run -d --name elasticsearch -p 9200:9200 -e "discovery.type=single-node" -e "xpack.security.enabled=false" -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" docker.elastic.co/elasticsearch/elasticsearch:8.10.0

# 安装IK中文分词器
docker exec -it elasticsearch elasticsearch-plugin install https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v8.10.0/elasticsearch-analysis-ik-8.10.0.zip

# 重启Elasticsearch
docker restart elasticsearch
```

**验证Elasticsearch运行：**
```bash
curl http://localhost:9200
```

### 3. 后端设置

```bash
# 进入backend目录
cd week6_hw/backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 4. 配置环境变量

创建 `.env` 文件在 `week6_hw` 目录：

```env
# OpenAI配置
OPENAI_API_KEY=sk-your-api-key-here

# Elasticsearch配置
ELASTICSEARCH_URL=http://localhost:9200

# 服务器配置
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# 数据目录配置
UPLOAD_DIR=./data/original
PROCESSED_DIR=./data/processed
OUTPUT_DIR=./data/output

# 执行配置
CODE_EXECUTION_TIMEOUT=60
MAX_FILE_SIZE=52428800
```

### 5. 初始化Elasticsearch索引

```bash
cd week6_hw/backend
python scripts/init_es_index.py
```

### 6. 启动后端服务

```bash
cd week6_hw/backend
python main.py
```

后端将运行在: http://localhost:8000
API文档: http://localhost:8000/docs

### 7. 启动前端

打开新终端：

```bash
cd week6_hw/frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将运行在: http://localhost:3000

## 📝 使用指南

### 上传Excel文件

1. 打开浏览器访问 http://localhost:3000
2. 使用REST API上传文件：

```bash
curl -X POST http://localhost:8000/api/files/upload \
  -F "file=@your_excel_file.xlsx"
```

或使用Python：

```python
import requests

with open('your_file.xlsx', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/files/upload',
        files={'file': f}
    )
    print(response.json())
```

### 通过聊天界面提问

1. 在输入框输入问题，例如：
   - "分析一下销售数据的趋势"
   - "统计每个地区的总销售额"
   - "画一个柱状图展示各产品的销量"

2. 或点击语音按钮进行语音提问

3. 系统将自动：
   - 检索相关Excel文件
   - 生成Python分析代码
   - 执行代码并返回结果
   - 展示数据溯源信息

## 🔧 API接口

### REST API

**上传文件：**
```
POST /api/files/upload
Content-Type: multipart/form-data
```

**获取文件列表：**
```
GET /api/files
```

**获取文件详情：**
```
GET /api/files/{file_id}
```

**健康检查：**
```
GET /health
```

### WebSocket

**聊天端点：**
```
ws://localhost:8000/ws/chat
```

**消息格式：**
```json
{
  "type": "text",
  "content": "用户问题"
}
```

## 🎨 技术栈

**后端：**
- FastAPI - 现代高性能Web框架
- OpenAI GPT-4 - 代码生成
- Elasticsearch 8.x - 混合检索
- pandas + openpyxl - Excel处理
- asyncio - 异步处理

**前端：**
- React 18 - UI框架
- Ant Design - 组件库
- WebSocket - 实时通信
- Web Speech API - 语音识别
- react-syntax-highlighter - 代码高亮

## 📊 示例问题

- "这个文件包含什么数据？"
- "计算销售额的平均值"
- "按地区统计订单数量"
- "找出销售额最高的前10个产品"
- "画一个折线图显示每月的销售趋势"
- "分析客户年龄分布"
- "计算各部门的预算总和"

## ⚠️ 注意事项

1. **OpenAI API费用**：系统会调用GPT-4和Embedding API，请注意API使用成本
2. **Elasticsearch内存**：建议至少分配512MB内存
3. **代码执行安全**：系统会检查危险代码，但仍建议在受控环境使用
4. **浏览器兼容性**：语音输入功能需要Chrome/Edge等支持Web Speech API的浏览器

## 🐛 故障排除

### Elasticsearch连接失败
```bash
# 检查ES是否运行
curl http://localhost:9200

# 查看ES日志
docker logs elasticsearch
```

### 后端启动失败
```bash
# 检查环境变量
cat .env

# 检查Python依赖
pip list

# 查看详细错误
python -m backend.main
```

### 前端无法连接WebSocket
- 确保后端已启动在8000端口
- 检查浏览器控制台错误
- 尝试刷新页面重新连接

## 📄 许可证

MIT License

## 👥 贡献

欢迎提交Issue和Pull Request！

## 📧 联系

如有问题，请创建GitHub Issue。

