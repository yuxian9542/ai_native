# 📊 Excel文件上传功能使用指南

## 🎯 功能概述
系统支持用户上传Excel文件，自动进行数据清洗和Elasticsearch索引，为后续的智能分析做准备。

## 🚀 使用方法

### 通过Web界面上传
1. 启动系统后访问 http://localhost:5173
2. 点击左侧面板的"上传Excel"按钮
3. 选择Excel文件（.xlsx或.xls）
4. 等待上传和处理完成
5. 文件将出现在左侧文件列表中

### 通过API上传
```bash
curl -X POST "http://localhost:8000/files/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_file.xlsx"
```

## 📁 文件处理流程
1. **上传**：文件保存到 `data/original/` 目录
2. **预处理**：智能识别表头、处理合并单元格
3. **清洗**：保存到 `data/processed/` 目录
4. **索引**：生成元数据并存储到Elasticsearch
5. **完成**：文件可用于智能分析

## 🔧 支持的文件格式
- Excel 2007+ (.xlsx)
- Excel 97-2003 (.xls)

## 📊 文件信息
- 文件名和大小
- 行数和列数
- 上传时间
- 处理状态

## 🗑️ 文件管理
- 查看已上传文件列表
- 删除不需要的文件
- 文件状态实时更新

## ⚠️ 注意事项
- 文件大小限制：50MB
- 支持中文文件名
- 自动处理复杂表头
- 保留原始文件备份