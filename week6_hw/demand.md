# Excel智能分析系统 - 完整需求文档（无Docker版本）

---

## 一、项目概述

### 1.1 项目名称
Excel智能分析系统（Excel Intelligent Analysis System）

### 1.2 项目目标
构建一个基于Web的智能数据分析平台，用户通过自然语言（支持文字和语音输入）提问，系统自动从知识库中检索相关Excel文件，生成Python分析代码并安全执行，返回可视化结果和完整的数据溯源信息。

### 1.3 核心价值
- 零代码数据分析：非技术人员可通过自然语言完成复杂数据分析
- 智能文件匹配：自动从多个Excel文件中选择最相关的数据源
- 全程可追溯：清晰展示使用的文件、列、代码和分析逻辑
- 实时交互体验：WebSocket实现流式输出，语音输入提升便捷性

---

## 二、技术栈确定

### 2.1 后端技术栈
- **Web框架**: FastAPI（选择理由：原生异步支持，内置WebSocket，性能优于Flask）
- **大语言模型**: OpenAI GPT-4（代码生成） + text-embedding-ada-002（语义检索）openai_api 在.env file
- **搜索引擎**: Elasticsearch 8.x 
- **Excel处理**: pandas + openpyxl
- **代码执行**: subprocess + 限制机制（无需Docker，使用进程隔离和权限限制）
- **异步处理**: asyncio + aiofiles

### 2.2 前端技术栈
- **框架**: React 18+（选择理由：虚拟DOM适合频繁更新，组件化便于维护）
- **UI库**: Ant Design（企业级组件库，开箱即用）
- **WebSocket**: 原生WebSocket API
- **语音输入**: Web Speech API（浏览器原生支持）
- **代码高亮**: react-syntax-highlighter
- **图表展示**: recharts或echarts-for-react

### 2.3 数据存储
- **原始Excel**: 文件系统 ./data/original/
- **处理后CSV**: 文件系统 ./data/processed/
- **生成的图表**: 文件系统 ./data/output/
- **元数据和索引**: Elasticsearch

---

## 三、系统架构设计

### 3.1 整体架构图
```
用户浏览器
    ↓ (HTTP/WebSocket)
FastAPI后端服务
    ↓
├─ Excel预处理模块
├─ 元数据生成模块
├─ Elasticsearch检索模块
├─ OpenAI代码生成模块
└─ 代码执行模块（subprocess隔离）
    ↓
数据存储层
├─ 文件系统（Excel、CSV、图片）
└─ Elasticsearch（元数据、向量索引）
```

### 3.2 数据流转流程
1. 用户上传Excel → 预处理 → 生成元数据 → 索引到ES
2. 用户提问 → ES混合检索 → 返回相关文件
3. LLM生成代码 → subprocess执行 → 返回结果和图表
4. WebSocket实时推送各阶段状态

---

## 四、详细功能需求

### 功能模块1：Excel文件预处理

#### 需求背景
真实业务中的Excel文件通常包含大量非数据内容（标题、说明、空行、多级表头、合并单元格等），需要自动清理并转换为标准二维表。

#### 具体需求

**需求1.1：智能识别无关行**
- 读取Excel文件的前20行作为样本
- 调用OpenAI GPT-4分析样本，识别：
  - 标题行（如"XX公司2024年销售报表"）
  - 空白行
  - 注释说明行（如"备注：数据截至..."）
  - 真正的数据表头行号
- 返回需要跳过的行号列表和表头行号
- 提示词要求返回JSON格式便于解析

**需求1.2：多级表头合并**
- 使用openpyxl读取Excel文件的合并单元格信息
- 识别2-3层表头结构（例如：第1层"销售数据"、第2层"金额"）
- 自动检测每一列对应的各级表头内容
- 用下划线连接各级表头，生成最终列名
- 示例转换：
  ```
  原始表头：
  层1: [  销售数据  ][  成本数据  ]
  层2: [金额][数量][金额][数量]
  
  转换结果：
  ["销售数据_金额", "销售数据_数量", "成本数据_金额", "成本数据_数量"]
  ```

**需求1.3：拆分合并单元格**
- 遍历Excel中所有合并单元格区域
- 获取合并区域左上角单元格的值
- 拆分合并单元格
- 用原值填充所有拆分后的单元格
- 示例：A1:A3合并值为"北京" → 拆分后A1、A2、A3都为"北京"

**需求1.4：输出标准二维表**
- 删除全空行和全空列
- 确保列名唯一且无空值（重复列名自动添加后缀）
- 保存为UTF-8编码的CSV文件到processed目录
- 记录处理日志（跳过的行数、合并的表头数等）

---

### 功能模块2：元数据生成与索引

#### 需求背景
为每个Excel文件生成"数据指纹"，包含摘要、列描述、统计信息、语义向量等，用于后续智能检索。

#### Elasticsearch索引设计需求

**索引名称**: excel_metadata

**字段结构要求**:
1. **基础信息字段**
   - file_id: keyword类型，唯一标识符（UUID）
   - file_name: text类型，使用ik_max_word分词器，同时保留keyword子字段
   - file_path: keyword类型，原始文件路径
   - processed_path: keyword类型，处理后CSV路径

2. **内容描述字段**
   - summary: text类型，使用ik_smart分词器，LLM生成的50字内摘要

3. **列信息字段**（nested类型）
   - columns: 数组，每个元素包含：
     - name: text类型（ik_max_word分词），列名
     - type: keyword类型，数据类型（int64/float64/object等）
     - description: text类型（ik_smart分词），LLM生成的10字内描述
     - sample_values: keyword类型数组，3个样本值
     - unique_count: integer类型，唯一值数量
     - null_count: integer类型，空值数量


4. **向量检索字段**
   - embedding: dense_vector类型，1536维，使用cosine相似度

5. **元数据字段**
   - tags: keyword类型数组，标签（可选）
   - created_at: date类型，创建时间
   - updated_at: date类型，更新时间

**索引配置要求**:
- 分片数：1（单节点部署）
- 副本数：0（开发环境）
- 需要安装elasticsearch-analysis-ik插件支持中文分词

#### 元数据生成需求

**需求2.1：生成数据摘要**
- 输入：处理后的DataFrame + 文件名
- 调用OpenAI GPT-4生成50字内的中文摘要
- 摘要需包含：数据类型、主要用途、时间/地域范围（如果有）
- 提示词要求简洁明了，避免冗长描述

**需求2.2：生成列描述**
- 为每一列调用OpenAI生成10字内描述
- 提供的信息：列名、数据类型、非空数量、唯一值数量、5个样本值
- 描述需说明该列代表的业务含义
- 批量处理以提高效率（可以一次请求处理多列）


**需求2.4：生成语义向量**
- 拼接以下文本生成embedding：
  - 文件名
  - 摘要
  - 所有列名（逗号分隔）
  - 潜在问题（逗号分隔）
- 调用OpenAI text-embedding-ada-002模型
- 返回1536维向量

**需求2.5：索引到Elasticsearch**
- 将完整的元数据文档索引到excel_metadata索引
- 使用file_id作为文档ID
- 索引成功后返回file_id

---

### 功能模块3：智能文件检索

#### 需求背景
用户提问后，需要从可能的数十上百个Excel文件中找到最相关的数据源。

#### 检索策略需求

**需求3.1：混合检索算法**
- 同时使用关键词检索（BM25）和语义向量检索（Cosine Similarity）
- 权重分配：
  - 向量相似度得分 × 10
  - BM25关键词得分 × 0.3
- 最终得分 = 向量得分 + 关键词得分

**需求3.2：多字段搜索**
- 关键词搜索字段及权重：
  - file_name: 权重3（最重要）
  - summary: 权重2
  - columns.name: 权重2
  - columns.description: 权重1
  - potential_questions: 权重1
- 使用multi_match查询类型为best_fields
- 启用模糊匹配（fuzziness: AUTO）

**需求3.3：向量相似度计算**
- 将用户问题转换为embedding（1536维向量）
- 使用script_score查询计算余弦相似度
- 公式：cosineSimilarity(question_vector, 'embedding')

**需求3.4：返回结果要求**
- 默认返回Top 3相关文件
- 每个结果包含：
  - 相关度得分
  - 文件基本信息（ID、名称、路径）
  - 摘要和列信息
  - 高亮匹配的关键词（highlight功能）
- 按得分降序排列

**需求3.5：无结果处理**
- 如果检索不到任何文件，返回友好提示
- 建议用户：上传相关数据文件或调整问题描述

---

### 功能模块4：Python代码生成

#### 需求背景
根据用户问题和选中的数据文件，自动生成可执行的Python分析代码。

#### 代码生成需求

**需求4.1：提示词工程**
- 角色设定：专业的Python数据分析师
- 提供的上下文信息：
  - 用户的原始问题
  - 选中文件的元数据（文件名、摘要、列信息、统计信息）
  - 每列的类型、描述、样本值
- 要求的输出格式：JSON格式包含code、used_columns、analysis_type、expected_output

**需求4.2：代码规范要求**
1. **文件路径处理**
   - CSV文件路径使用变量：CSV_FILE_PATH（执行时替换为实际路径）
   - 输出图片路径使用变量：OUTPUT_IMAGE_PATH（执行时替换）

2. **基础导入和配置**
   - 必须导入pandas、numpy
   - 如需可视化，导入matplotlib
   - 设置matplotlib中文字体：plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
   - 使用非交互式后端：matplotlib.use('Agg')

3. **数据处理要求**
   - 处理可能的空值（dropna、fillna）
   - 处理数据类型转换异常（try-except）
   - 对异常数据进行清洗

4. **输出要求**
   - 使用print()输出清晰的文字描述
   - 说明分析发现的关键结论
   - 如生成图表，保存为PNG格式到OUTPUT_IMAGE_PATH
   - 图表需包含标题、坐标轴标签、图例

5. **安全限制**
   - 不能使用input()等交互操作
   - 不能进行文件写入（除了指定的图片路径）
   - 不能使用os、subprocess、sys等系统模块
   - 仅允许使用：pandas、numpy、matplotlib、scipy、sklearn等数据分析库

**需求4.3：返回格式**
返回JSON，包含以下字段：
- code: 完整的Python代码字符串
- used_columns: 实际使用的列名列表（用于溯源）
- analysis_type: 分析类型描述（如"趋势分析"、"统计汇总"）
- expected_output: 预期输出描述

**需求4.4：LLM调用参数**
- model: gpt-4
- temperature: 0.2（保持生成稳定性）
- max_tokens: 2000
- 如果返回的不是纯JSON，需要使用正则提取JSON部分

---

### 功能模块5：安全代码执行（无Docker版本）

#### 需求背景
在不使用Docker的情况下，通过subprocess和权限限制实现代码安全执行。

#### 执行方案需求

**需求5.1：临时工作目录**
- 每次执行创建独立的临时目录（使用tempfile.mkdtemp）
- 目录命名：analysis_{uuid}
- 执行完成后自动清理

**需求5.2：代码安全检查**
在执行前进行静态检查，如果代码包含以下内容则拒绝执行：
- import os
- import subprocess
- import sys
- from os import
- from subprocess import
- __import__
- eval()
- exec()
- open() with write mode（除了指定的输出路径）

**需求5.3：代码增强**
执行前在用户代码前添加安全头部：
```
导入警告抑制
导入基础库（pandas、numpy、matplotlib）
设置matplotlib非交互式后端
设置中文字体
```

**需求5.4：subprocess执行**
- 使用asyncio.create_subprocess_exec执行python
- 工作目录：临时目录
- 超时时间：60秒（可配置）
- 捕获标准输出和标准错误
- 执行命令：python script.py

**需求5.5：结果收集**
- 收集stdout作为分析输出
- 收集stderr作为错误信息
- 检查临时目录是否生成了output.png
- 如果有图片，读取并转为base64编码
- 根据returncode判断执行成功与否

**需求5.6：异常处理**
- 执行超时：返回超时错误信息
- Python运行错误：返回stderr内容
- 文件读取错误：返回相应错误
- 所有异常都返回统一格式的错误字典

**需求5.7：资源清理**
- 无论执行成功或失败，都删除临时目录
- 使用shutil.rmtree清理
- 清理失败不影响返回结果

**需求5.8：返回格式**
返回字典包含：
- success: 布尔值，是否成功
- output: 标准输出内容（成功时）
- image: base64编码的图片（如果有）
- error: 错误信息（失败时）

---

### 功能模块6：WebSocket实时通信

#### 需求背景
提供实时双向通信，让用户可以实时看到分析的各个阶段进展。

#### WebSocket需求

**需求6.1：连接管理**
- 使用FastAPI内置的WebSocket支持
- 端点路径：/ws/chat
- 每个连接分配唯一client_id（UUID）
- 维护活跃连接字典
- 连接断开时自动清理

**需求6.2：消息类型定义**

**客户端发送消息格式**:
```json
{
  "type": "text" 或 "voice",
  "content": "用户问题或语音转文字结果"
}
```

**服务器响应消息类型**:

1. **状态消息** (type: "status")
```json
{
  "type": "status",
  "content": "正在检索相关文件..." / "正在生成代码..." / "正在执行分析..."
}
```

2. **文件检索结果** (type: "files_found")
```json
{
  "type": "files_found",
  "content": {
    "files": [
      {
        "name": "文件名",
        "summary": "摘要",
        "score": 相关度得分
      }
    ]
  }
}
```

3. **代码生成结果** (type: "code_generated")
```json
{
  "type": "code_generated",
  "content": {
    "code": "Python代码",
    "used_columns": ["列1", "列2"],
    "analysis_type": "分析类型"
  }
}
```

4. **最终结果** (type: "analysis_complete")
```json
{
  "type": "analysis_complete",
  "content": {
    "success": true,
    "output": "文字输出",
    "image": "base64图片（如果有）",
    "used_file": "使用的文件名",
    "used_columns": ["列1", "列2"],
    "code": "执行的代码",
    "file_summary": "文件摘要"
  }
}
```

5. **错误消息** (type: "error")
```json
{
  "type": "error",
  "content": "错误描述"
}
```

**需求6.3：完整处理流程**
用户发送问题后，服务器依次执行：
1. 发送"正在检索相关文件..."状态
2. 调用检索服务，发送files_found消息
3. 发送"正在生成分析代码..."状态
4. 调用代码生成服务，发送code_generated消息
5. 发送"正在执行分析..."状态
6. 调用代码执行服务，发送analysis_complete或error消息

**需求6.4：错误处理**
- 捕获所有异常并发送error类型消息
- 错误消息包含异常描述和堆栈跟踪（开发环境）
- 任何步骤失败都停止后续流程
- 设置isProcessing状态为false

---

### 功能模块7：React前端界面

#### 需求背景
构建用户友好的Web界面，支持文字输入、语音输入、实时消息展示。

#### 前端功能需求

**需求7.1：整体布局**
- 使用Ant Design的Layout组件
- Header: 显示标题"Excel智能分析系统"和连接状态
- Content: 消息展示区域（可滚动）
- Footer: 输入区域（文字输入框 + 发送按钮 + 语音按钮）

**需求7.2：WebSocket连接**
- 组件挂载时自动连接到ws://localhost:8000/ws/chat
- 连接成功显示绿色状态指示
- 连接断开显示红色状态并提示
- 监听onmessage事件处理服务器消息
- 组件卸载时关闭连接

**需求7.3：消息展示**
根据消息类型使用不同的卡片样式展示：

1. **用户消息**
   - 右对齐，蓝色背景
   - 显示"🧑 你："+ 消息内容

2. **状态消息**
   - 灰色背景，显示加载图标
   - 内容：状态文字

3. **文件检索结果**
   - 标题："📁 找到相关文件"
   - 列表展示每个文件的名称、摘要、匹配度

4. **代码展示**
   - 标题："💻 生成的分析代码"
   - 使用react-syntax-highlighter高亮Python代码
   - 显示使用的列和分析类型

5. **分析结果**
   - 标题："📊 分析结果"
   - 文字输出区域（pre标签保留格式）
   - 图片展示区域（如果有）
   - 数据溯源信息（使用的文件、列）

6. **错误消息**
   - 红色背景，显示错误图标
   - 错误描述文字

**需求7.4：输入功能**

1. **文字输入**
   - TextArea组件，支持多行
   - 回车发送（Ctrl+Enter换行）
   - 发送按钮（SendOutlined图标）
   - 发送后清空输入框

2. **语音输入**
   - 使用Web Speech API
   - 点击麦克风图标开始录音
   - 录音中显示红色麦克风图标+波纹动画
   - 识别完成后自动填充到输入框
   - 再次点击停止录音
   - 语言设置：zh-CN

**需求7.5：状态管理**
使用React Hooks管理以下状态：
- messages: 消息列表数组
- inputValue: 输入框内容
- isConnected: WebSocket连接状态
- isListening: 语音识别状态
- isProcessing: 正在处理请求状态（禁用发送按钮）

**需求7.6：自动滚动**
- 新消息添加时自动滚动到底部
- 使用useRef + scrollIntoView实现

**需求7.7：响应式设计**
- 适配桌面端（1920x1080）
- 适配平板端（768x1024）
- 移动端基本可用（375x667）

---

### 功能模块8：REST API

#### 需求背景
除了WebSocket聊天，还需要REST API支持文件上传、列表查询等操作。

#### API端点需求

**API 1：上传Excel文件**
```
POST /api/files/upload
Content-Type: multipart/form-data

请求参数:
- file: 上传的Excel文件（.xlsx或.xls）

处理流程:
1. 验证文件类型
2. 保存到./data/original/目录
3. 调用Excel预处理服务
4. 生成元数据并索引到ES
5. 返回file_id

成功响应:
{
  "success": true,
  "file_id": "uuid",
  "file_name": "文件名.xlsx",
  "message": "文件上传并处理成功"
}

失败响应:
{
  "success": false,
  "error": "错误描述"
}
```

**API 2：获取文件列表**
```
GET /api/files

响应:
{
  "files": [
    {
      "file_id": "uuid",
      "file_name": "文件名",
      "summary": "摘要",
      "row_count": 1000,
      "column_count": 10,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

**API 3：获取文件详情**
```
GET /api/files/{file_id}

响应:
{
  "file_id": "uuid",
  "file_name": "文件名",
  "summary": "摘要",
  "columns": [...],
  "statistics": {...},
  "potential_questions": [...]
}
```

**API 4：健康检查**
```
GET /health

响应:
{
  "status": "healthy",
  "elasticsearch": true,
  "openai": "connected"
}
```

---

## 五、项目结构要求

```
excel-analysis-system/
├── backend/                    # 后端目录
│   ├── main.py                # FastAPI主应用入口
│   ├── config.py              # 配置文件（从环境变量读取）
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py         # Pydantic数据模型
│   │   └── elasticsearch.py   # ES索引定义（mapping）
│   ├── services/              # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── excel_processor.py       # Excel预处理服务
│   │   ├── metadata_generator.py    # 元数据生成服务
│   │   ├── file_retriever.py        # 文件检索服务
│   │   ├── code_generator.py        # 代码生成服务
│   │   └── code_executor.py         # 代码执行服务
│   ├── api/                   # API层
│   │   ├── __init__.py
│   │   ├── rest.py           # REST API路由
│   │   └── websocket.py      # WebSocket处理
│   ├── utils/                 # 工具类
│   │   ├── __init__.py
│   │   ├── openai_client.py   # OpenAI API封装
│   │   └── es_client.py       # Elasticsearch客户端封装
│   ├── scripts/               # 脚本工具
│   │   └── init_es_index.py  # 初始化ES索引脚本
│   └── requirements.txt       # Python依赖
│
├── frontend/                   # 前端目录
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.jsx           # 主应用组件
│   │   ├── App.css           # 样式文件
│   │   ├── components/       # 组件目录
│   │   │   ├── ChatHistory.jsx      # 消息历史组件
│   │   │   ├── MessageItem.jsx      # 单条消息组件
│   │   │   ├── InputArea.jsx        # 输入区域组件
│   │   │   └── VoiceButton.jsx      # 语音按钮组件
│   │   ├── hooks/            # 自定义Hooks
│   │   │   ├── useWebSocket.js      # WebSocket Hook
│   │   │   └── useSpeechRecognition.js  # 语音识别Hook
│   │   ├── utils/
│   │   │   └── api.js        # API调用封装
│   │   └── index.js          # 入口文件
│   ├── package.json          # 前端依赖
│   └── vite.config.js        # Vite配置（或webpack.config.js）
│
├── data/                      # 数据目录
│   ├── original/             # 原始Excel文件
│   ├── processed/            # 处理后CSV文件
│   └── output/               # 生成的图表等
│
├── .env.example              # 环境变量示例
├── .gitignore
├── README.md                 # 项目说明文档
└── requirements.txt          # 全局Python依赖（可选）
```

---

## 六、配置和环境变量

### 需要的环境变量（.env文件）
```
# OpenAI配置
OPENAI_API_KEY=sk-...

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
MAX_FILE_SIZE=52428800  # 50MB
```

---

## 七、依赖库清单

### 后端依赖（requirements.txt）
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
pydantic==2.5.0
pydantic-settings==2.1.0

openai==1.3.0
elasticsearch==8.11.0

pandas==2.1.3
openpyxl==3.1.2
numpy==1.26.2

aiofiles==23.2.1
python-dotenv==1.0.0
```

### 前端依赖（package.json）
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "antd": "^5.11.0",
    "@ant-design/icons": "^5.2.6",
    "react-syntax-highlighter": "^15.5.0",
    "react-markdown": "^9.0.1",
    "recharts": "^2.10.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.0",
    "vite": "^5.0.0"
  }
}
```

---

## 八、部署和启动流程

### 8.1 Elasticsearch部署
**方式1：使用Docker（推荐）**
```bash
docker run -d \
  --name elasticsearch \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" \
  docker.elastic.co/elasticsearch/elasticsearch:8.10.0

# 安装ik分词器
docker exec -it elasticsearch \
  elasticsearch-plugin install \
  https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v8.10.0/elasticsearch-analysis-ik-8.10.0.zip

# 重启
docker restart elasticsearch
```

**方式2：本地安装**
- 下载Elasticsearch 8.10.0
- 修改config/elasticsearch.yml禁用安全认证
- 安装ik分词器插件
- 启动服务

### 8.2 后端启动
```bash
# 1. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑.env文件，填入OPENAI_API_KEY

# 4. 初始化ES索引
python backend/scripts/init_es_index.py

# 5. 启动后端
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 8.3 前端启动
```bash
cd frontend
npm install
npm run dev
```

### 8.4 访问地址
- 前端界面：http://localhost:3000
- 后端API文档：http://localhost:8000/docs
- Elasticsearch：http://localhost:9200

---

## 九、测试需求

### 9.1 单元测试需求
- Excel预处理模块测试（准备3-5个复杂Excel样例）
- 元数据生成测试（mock OpenAI响应）
- 代码执行安全性测试（测试危险代码被拦截）
- Elasticsearch检索测试（测试混合检索准确性）

### 9.2 集成测试需求
- 完整流程测试：上传 → 检索 → 生成 → 执行
- WebSocket连接测试
- 并发请求测试（10个并发用户）
- 错误处理测试（网络异常、ES宕机等）

### 9.3 性能测试需求
- 单个Excel文件处理时间：<30秒
- 元数据生成时间：<1分钟
- 代码生成时间：<10秒
- 代码执行时间：<60秒
- WebSocket消息延迟：<100ms

---

## 十、需要补充的信息

### 请明确以下问题：

1. **OpenAI API配置**
   - 是否已有OpenAI API Key？
   - API调用限制是多少（RPM/TPM）？
   - 是否需要配置代理访问？

2. **数据规模预期**
   - 预计管理多少个Excel文件？（10个/100个/1000个？）
   - 单个Excel文件最大行数？
   - 是否需要支持超大文件（>100MB）？

3. **用户权限**
   - 是否需要用户登录认证？
   - 是否需要区分用户权限（管理员/普通用户）？
   - 是否需要多租户隔离？

4. **部署环境**
   - 部署在本地服务器还是云端？
   - 服务器配置？（CPU/内存/磁盘）
   - 操作系统？（Linux推荐，Windows需调整部分代码）

5. **安全要求**
   - 是否需要HTTPS？
   - 是否需要API访问限流？
   - 是否需要审计日志（记录所有操作）？

6. **扩展需求**
   - 未来是否需要支持其他文件格式（CSV、TXT、JSON）？
   - 是否需要支持数据库连接（MySQL、PostgreSQL）？
   - 是否需要定时任务（自动更新数据）？

7. **UI/UX偏好**
   - 是否有品牌色要求？
   - 是否需要暗色模式？
   - 是否需要移动端优化？

8. **错误恢复**
   - Excel处理失败后是否允许手动调整？
   - 代码执行失败后是否允许用户修改代码重试？
   - 是否需要保存历史对话记录？

9. **监控和日志**
   - 是否需要日志记录系统（logging）？
   - 是否需要性能监控（APM）？
   - 是否需要错误告警？

10. **开发时间预期**
    - 项目交付时间要求？
    - 是否分阶段交付（MVP → 完整版）？

---

## 十一、成功标准

### 功能完整性
- ✅ 能成功上传并处理复杂Excel文件
- ✅ 能准确检索到相关文件
- ✅ 能生成正确的Python分析代码
- ✅ 能安全执行代码并返回结果
- ✅ WebSocket实时通信流畅
- ✅ 语音输入功能正常

### 性能指标
- ✅ 单文件处理时间 < 30秒
- ✅ 查询响应时间 < 5秒
- ✅ 代码执行时间 < 60秒
- ✅ 界面无明显卡顿

### 用户体验
- ✅ 界面简洁友好
- ✅ 错误提示清晰
- ✅ 数据溯源完整
- ✅ 支持语音输入

### 代码质量
- ✅ 代码结构清晰
- ✅ 注释充分
- ✅ 错误处理完善
- ✅ 遵循最佳实践

---

**以上是完整的需求文档，请确认是否有遗漏或需要调整的部分。确认后即可开始代码实现。**