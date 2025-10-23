# 📊 Excel文件上传功能使用指南

## 🎯 功能概述

系统现在支持用户上传Excel文件，自动进行数据清洗和Elasticsearch索引，为后续的智能分析做准备。

## 🚀 使用方法

### 方法1: 通过Web界面上传

1. **启动系统**:
   ```bash
   # 启动后端
   cd week6_hw
   python -c "from backend.main import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8000)"
   
   # 启动前端 (新终端)
   cd week6_hw/frontend
   npm install
   npm run dev
   ```

2. **访问界面**: http://localhost:3000

3. **上传文件**:
   - 点击右上角的"上传Excel"按钮
   - 选择.xlsx或.xls文件
   - 等待处理完成（会显示进度条）

### 方法2: 通过测试页面

1. **打开测试页面**: 在浏览器中打开 `week6_hw/test_upload.html`

2. **上传文件**:
   - 拖拽Excel文件到上传区域
   - 或点击"选择文件"按钮

### 方法3: 通过API直接上传

```bash
curl -X POST http://localhost:8000/api/files/upload \
  -F "file=@your_file.xlsx"
```

## 🔄 处理流程

上传的Excel文件会经过以下处理：

### 1. 文件验证
- ✅ 检查文件类型（仅支持.xlsx和.xls）
- ✅ 生成唯一文件ID

### 2. 文件保存
- 📁 原始文件保存到 `data/original/`
- 📁 处理后文件保存到 `data/processed/`

### 3. Excel预处理
- 🤖 使用GPT-4识别无关行（标题、空行、注释）
- 🔧 拆分合并单元格
- 📊 处理多级表头（合并为单级）
- 🧹 清理数据（删除空行空列）
- 💾 转换为标准CSV格式

### 4. 元数据生成
- 📝 使用GPT-4生成文件摘要（50字内）
- 📋 生成列描述（每列10字内业务含义）
- 📊 统计列信息（类型、唯一值、空值等）
- 🧠 生成语义向量（text-embedding-ada-002）

### 5. Elasticsearch索引
- 🔍 存储到excel_metadata索引
- 🔎 支持混合检索（BM25 + 向量相似度）

## 📱 界面功能

### 上传界面
- **上传按钮**: 右上角绿色"上传Excel"按钮
- **进度显示**: 实时显示上传和处理进度
- **文件计数**: 显示已上传文件数量

### 欢迎页面
- **文件列表**: 显示所有已上传的文件
- **文件信息**: 文件名、上传时间、处理状态

### 聊天界面
- **上传成功消息**: 自动显示上传成功的通知
- **文件状态**: 显示文件已清洗并索引到ES

## 🔧 API接口

### 上传文件
```
POST /api/files/upload
Content-Type: multipart/form-data
Body: file (Excel文件)
Response: {
  "success": true,
  "file_id": "uuid",
  "file_name": "filename.xlsx",
  "message": "文件上传并处理成功"
}
```

### 获取文件列表
```
GET /api/files
Response: {
  "files": [
    {
      "file_id": "uuid",
      "file_name": "filename.xlsx",
      "summary": "文件摘要",
      "row_count": 1000,
      "column_count": 10,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### 获取文件详情
```
GET /api/files/{file_id}
Response: {
  "file_id": "uuid",
  "file_name": "filename.xlsx",
  "summary": "文件摘要",
  "columns": [...],
  "statistics": {...}
}
```

## 📊 测试数据

系统已包含测试Excel文件：
- `data/original/cola.xlsx` - 可乐销售数据
- `data/original/复杂表头.xlsx` - 多级表头测试
- `data/original/发电日志.xlsx` - 发电数据
- 其他测试文件...

## 🐛 故障排除

### 上传失败
1. **检查文件格式**: 确保是.xlsx或.xls文件
2. **检查文件大小**: 建议小于50MB
3. **检查后端状态**: 确保后端服务正在运行
4. **检查网络**: 确保前端能访问后端API

### 处理失败
1. **检查OpenAI API**: 确保API密钥有效
2. **检查Elasticsearch**: 确保ES服务运行正常
3. **查看后端日志**: 检查具体错误信息

### 文件无法显示
1. **刷新页面**: 重新加载文件列表
2. **检查ES索引**: 确保文件已正确索引
3. **重新上传**: 尝试重新上传文件

## 📈 性能优化

- **文件大小**: 建议单个文件小于50MB
- **并发上传**: 支持多个文件同时上传
- **处理时间**: 大文件处理可能需要1-2分钟
- **内存使用**: 系统会自动管理内存使用

## 🔒 安全特性

- **文件类型验证**: 仅允许Excel文件
- **路径安全**: 使用安全的文件路径处理
- **代码执行**: 预处理过程在安全环境中进行
- **数据隔离**: 每个文件独立处理

## 📝 下一步

上传文件后，您可以：
1. **提问分析**: 在聊天界面输入问题
2. **查看文件**: 浏览已上传的文件列表
3. **获取详情**: 查看文件的详细信息和列结构
4. **开始分析**: 让AI帮您分析数据

---

**系统已准备就绪！** 🎉 开始上传您的Excel文件吧！
