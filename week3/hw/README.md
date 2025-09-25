# PDF RAG Pipeline - 完整的文档问答系统

一个功能完整的PDF文档检索增强生成(RAG)流水线，支持多模态内容处理、混合搜索和交互式问答。

## 🎯 核心功能

### ✅ 完整的8步RAG流水线

1. **🚀 本地部署 Elasticsearch** - 自动检查和创建索引
2. **📄 PDF处理** - 提取文本、图片和表格内容  
3. **✂️ 内容切分** - 智能分块，为图片生成描述
4. **🔢 向量化** - 为文本、表格摘要和图片描述生成向量
5. **📇 索引存储** - 将内容与向量存储到Elasticsearch
6. **🔍 混合搜索** - BM25关键词搜索 + 向量语义搜索
7. **🎯 重排序** - RRF融合 + 可选的reranker模型
8. **💬 答案生成** - 基于检索结果生成带引用的回答

### ✨ 高级特性

- **📚 批量处理** - 支持单个文件或整个目录的PDF批量加载
- **💬 交互式问答** - 支持多轮对话，包含指代消解
- **🔍 智能验证** - 自动检查索引状态，防止空查询
- **🗂️ 多模态支持** - 统一处理文本、图片、表格内容
- **⚡ 高性能** - 批量向量化和索引，内存优化
- **🛠️ 灵活配置** - 支持自定义参数和多索引管理

## 🏗️ 项目结构

```
week3/hw/
├── pipeline.py              # 🚀 主流水线
├── config.py               # 配置和Elasticsearch连接
├── document_process.py     # PDF文档处理
├── embedding.py            # 向量嵌入服务
├── es_functions.py         # Elasticsearch操作
├── image_table.py          # 图片和表格处理
├── retrieve_documents.py   # 检索和搜索
├── websearch.py           # 网络搜索
├── requirements.txt       # 依赖包
├── test_pdf/             # 测试PDF文件
└── README.md            # 项目说明
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install -r requirements.txt

# 配置API密钥
cp env_template.txt .env
# 编辑.env文件，添加你的API密钥
```

### 2. 环境变量配置

创建 `.env` 文件：

```bash
# OpenAI API Key - 从 https://platform.openai.com/api-keys 获取
OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# Web Search API Key
WEB_SEARCH_KEY=your_web_search_key_here

# 可选：自定义服务URL
EMBEDDING_URL=http://test.2brain.cn:9800/v1/emb
RERANK_URL=http://test.2brain.cn:2260/rerank
IMAGE_MODEL_URL=http://test.2brain.cn:23333/v1
```

### 3. 启动Elasticsearch

确保Elasticsearch在本地运行（默认端口9200）。

## 📖 使用指南

### 基础用法

#### 1. 检查系统状态
```bash
python pipeline.py --status
```

#### 2. 完整流水线（处理+查询）
```bash
python pipeline.py --pdf document.pdf --query "什么是机器学习？"
```

#### 3. 仅加载文档到索引
```bash
# 单个文件
python pipeline.py --pdf document.pdf --load-only

# 批量加载目录
python pipeline.py --pdf-dir /path/to/pdfs --load-only

# 混合加载
python pipeline.py --pdf doc1.pdf --pdf-dir /path/to/pdfs --load-only
```

#### 4. 交互式问答模式
```bash
python pipeline.py --interactive
```

### 高级用法

#### 自定义参数
```bash
python pipeline.py \
  --pdf document.pdf \
  --query "查询问题" \
  --chunk-size 600 \
  --top-k 10 \
  --index-name custom_index
```

#### 多索引管理
```bash
# 法律文档索引
python pipeline.py --pdf-dir legal_docs/ --load-only --index-name legal_knowledge

# 技术文档索引  
python pipeline.py --pdf-dir tech_docs/ --load-only --index-name tech_knowledge

# 分别查询
python pipeline.py --interactive --index-name legal_knowledge
python pipeline.py --interactive --index-name tech_knowledge
```

## 💻 Python API

### 基础使用

```python
from pipeline import RAGPipeline

# 创建流水线实例
pipeline = RAGPipeline("my_knowledge_base")

# 方法1: 完整流水线
result = pipeline.run_complete_pipeline(
    pdf_path="document.pdf",
    query="什么是机器学习？"
)

if result["success"]:
    print("答案:", result["answer"])
    print("引用:", result["citations"])
```

### 分步执行

```python
# 方法2: 分步执行
pipeline.step1_deploy_elasticsearch()
pdf_result = pipeline.step2_process_pdf("document.pdf")
chunk_result = pipeline.step3_chunk_content(pdf_result["content"])
# ... 其他步骤

# 方法3: 仅加载文档
result = pipeline.load_documents_only(["doc1.pdf", "doc2.pdf"])

# 方法4: 交互式问答
pipeline.interactive_qa()
```

### 批量处理

```python
import glob

# 批量加载PDF
pdf_files = glob.glob("documents/*.pdf")
result = pipeline.load_documents_only(pdf_files, chunk_size=800)

if result["success"]:
    print(f"成功加载: {len(result['processed_files'])} 个文件")
    print(f"总文档块: {result['total_indexed']}")
    
    # 然后进行查询
    pipeline.interactive_qa()
```

## 🔧 配置选项

### 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--pdf` | PDF文件路径 | - |
| `--pdf-dir` | PDF目录路径 | - |
| `--query` | 查询问题 | - |
| `--load-only` | 仅加载模式 | False |
| `--interactive` | 交互模式 | False |
| `--status` | 检查索引状态 | False |
| `--index-name` | 索引名称 | "rag_pipeline_index" |
| `--chunk-size` | 分块大小 | 1024 |
| `--top-k` | 检索数量 | 10 |

### 环境变量

| 变量名 | 说明 | 必需 |
|--------|------|------|
| `OPENAI_API_KEY` | OpenAI API密钥 | 是 |
| `WEB_SEARCH_KEY` | 网络搜索API密钥 | 可选 |
| `EMBEDDING_URL` | 嵌入服务URL | 可选 |
| `RERANK_URL` | 重排序服务URL | 可选 |
| `IMAGE_MODEL_URL` | 图像模型URL | 可选 |

## 📊 工作流程示例

### 场景1: 建立新的知识库

```bash
# 1. 检查系统状态
python pipeline.py --status

# 2. 批量加载文档
python pipeline.py --pdf-dir documents/ --load-only --index-name company_docs

# 3. 验证加载结果
python pipeline.py --status --index-name company_docs

# 4. 开始查询
python pipeline.py --interactive --index-name company_docs
```

### 场景2: 增量更新知识库

```bash
# 1. 添加新文档
python pipeline.py --pdf new_document.pdf --load-only --index-name company_docs

# 2. 继续查询
python pipeline.py --interactive --index-name company_docs
```

### 场景3: 一次性处理和查询

```bash
# 直接处理并查询
python pipeline.py --pdf report.pdf --query "这份报告的主要结论是什么？"
```

## 🔍 功能特性详解

### 多模态内容处理

- **文本提取**: 使用PyMuPDF提取PDF文本内容
- **图片处理**: 自动提取图片并生成AI描述
- **表格识别**: 识别表格结构并转换为Markdown格式
- **上下文增强**: 结合页面上下文优化图片和表格描述

### 智能搜索系统

- **BM25搜索**: 基于关键词的精确匹配
- **向量搜索**: 基于语义相似度的智能检索
- **混合融合**: RRF算法融合多种搜索结果
- **重排序**: 可选的神经重排序模型优化

### 交互式体验

- **多轮对话**: 支持上下文记忆的连续问答
- **指代消解**: 自动处理"它"、"这个"等指代词
- **查询拆分**: 复杂问题自动分解为子问题
- **实时反馈**: 显示处理进度和响应时间

## 📈 性能优化

- **批量处理**: 向量化和索引采用批量操作
- **内存管理**: 分批处理大文档，避免内存溢出
- **并发支持**: 支持多索引并行运行
- **错误恢复**: 单个文件失败不影响批量处理

## 🛠️ 故障排除

### 常见问题

#### 1. Elasticsearch连接失败
```bash
# 检查Elasticsearch是否运行
curl -X GET "localhost:9200/"

# 检查连接配置
python pipeline.py --status
```

#### 2. API密钥错误
```bash
# 检查.env文件配置
cat .env

# 验证API密钥
python -c "from config import OPENAI_API_KEY; print('Key loaded:', bool(OPENAI_API_KEY))"
```

#### 3. 依赖包问题
```bash
# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

#### 4. 交互模式无法进入
```bash
# 检查索引状态
python pipeline.py --status

# 如果索引为空，先加载文档
python pipeline.py --pdf document.pdf --load-only
```

### 错误代码

| 错误信息 | 原因 | 解决方案 |
|----------|------|----------|
| "Elasticsearch连接失败" | ES未启动或配置错误 | 检查ES服务和config.py |
| "索引不存在" | 首次使用或索引被删除 | 使用--load-only加载文档 |
| "OpenAI API错误" | API密钥无效或额度不足 | 检查.env文件和账户余额 |
| "PDF处理失败" | 文件损坏或格式不支持 | 检查PDF文件完整性 |

## 📚 扩展功能

### 自定义处理器

```python
# 继承RAGPipeline类实现自定义功能
class CustomRAGPipeline(RAGPipeline):
    def custom_preprocessing(self, content):
        # 自定义预处理逻辑
        return processed_content
        
    def custom_postprocessing(self, results):
        # 自定义后处理逻辑
        return enhanced_results
```

### 插件系统

系统设计为模块化架构，可以轻松替换或扩展组件：

- **嵌入模型**: 更换不同的向量化服务
- **重排序器**: 集成其他重排序模型
- **文档处理器**: 支持更多文档格式
- **搜索引擎**: 支持其他向量数据库

## 🤝 贡献指南

欢迎提交Issues和Pull Requests！

### 开发环境设置

```bash
# 克隆项目
git clone <repository-url>
cd week3/hw

# 安装开发依赖
pip install -r requirements.txt

# 运行测试
python pipeline.py --status
```

## 📄 许可证

本项目基于MIT许可证开源。

## 🙏 致谢

- **Elasticsearch** - 强大的搜索和分析引擎
- **OpenAI** - 优秀的语言模型和API
- **LangChain** - 便捷的文档处理工具
- **PyMuPDF** - 高效的PDF处理库

---

## 📞 支持

如有问题或建议，请：

1. 查看本README的故障排除部分
2. 提交GitHub Issue
3. 查看项目Wiki文档

**Happy RAGing! 🚀**
