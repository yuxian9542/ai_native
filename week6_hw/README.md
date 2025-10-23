# Excel智能分析系统

基于AI的Excel数据分析平台，支持自然语言查询、智能文件检索、自动代码生成和安全执行。

## 🎯 核心功能

- ✅ **智能Excel预处理**：自动识别无关行、处理多级表头、拆分合并单元格
- ✅ **语义检索**：使用Elasticsearch混合检索（BM25 + 向量相似度）快速找到相关数据
- ✅ **AI代码生成**：GPT-4根据问题自动生成Python分析代码
- ✅ **安全执行**：虚拟环境执行代码，支持数据分析和可视化
- ✅ **实时通信**：WebSocket实时推送分析进度
- ✅ **语音输入**：支持语音提问，提升交互体验
- ✅ **数据溯源**：完整展示使用的文件、列和分析逻辑

## 🚀 快速开始

### 1. 环境准备
```bash
# 安装Python依赖
pip install -r backend/requirements.txt

# 安装前端依赖
cd frontend && npm install
```

### 2. 配置环境变量
```bash
# 复制环境变量模板
cp env.template .env

# 编辑.env文件，填入OpenAI API Key
OPENAI_API_KEY=your_api_key_here
```

### 3. 启动服务
```bash
# 启动后端
cd backend && python main.py

# 启动前端
cd frontend && npm run dev
```

### 4. 访问系统
- 前端界面：http://localhost:5173
- 后端API：http://localhost:8000

## 📁 项目结构

```
week6_hw/
├── backend/                 # 后端服务
│   ├── api/                # API接口
│   ├── services/           # 业务服务
│   ├── models/             # 数据模型
│   └── utils/              # 工具函数
├── frontend/               # 前端界面
│   └── src/                # React组件
├── data/                   # 数据目录
│   ├── original/           # 原始文件
│   ├── processed/          # 处理后文件
│   └── output/             # 分析结果
└── test/                   # 测试文件
```

## 🔧 技术栈

- **后端**：FastAPI + Elasticsearch + OpenAI GPT-4
- **前端**：React + Ant Design + WebSocket
- **数据**：pandas + openpyxl + matplotlib
- **执行**：虚拟环境 + subprocess

## 📖 使用指南

1. **上传文件**：在左侧文件管理面板上传Excel文件
2. **提问分析**：在输入框输入自然语言问题
3. **查看结果**：系统自动生成代码并执行分析
4. **管理文件**：在左侧面板管理已上传的文件

## 🛠️ 开发指南

### 运行测试
```bash
cd test
python run_all_tests.py
```

### 查看日志
```bash
# 后端日志
tail -f backend/logs/excel_analysis_*.log

# 测试日志
tail -f test/logs/excel_analysis_*.log
```

## 📝 更新日志

- ✅ 智能Excel预处理
- ✅ 语义检索和文件管理
- ✅ AI代码生成和重试机制
- ✅ 虚拟环境安全执行
- ✅ 前端侧边栏文件管理
- ✅ 详细错误日志和调试信息

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目！

## 📄 许可证

MIT License