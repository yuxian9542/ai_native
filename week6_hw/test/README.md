# 🧪 Excel智能分析系统 - 测试套件

本目录包含完整的测试脚本，用于验证系统的所有核心功能。

## 📁 测试文件说明

### 核心测试脚本

| 文件名 | 描述 | 功能 |
|--------|------|------|
| `run_all_tests.py` | 主测试脚本 | 运行所有测试 |
| `quick_test.py` | 快速测试 | 验证基本功能 |
| `test_backend.py` | 完整后端测试 | 测试所有后端功能 |
| `test_excel_processing.py` | Excel处理测试 | 测试Excel预处理和索引 |
| `test_code_execution.py` | 代码执行测试 | 测试代码生成和执行 |

## 🚀 使用方法

### 1. 运行所有测试

```bash
cd week6_hw/test
python run_all_tests.py
```

### 2. 运行单个测试

```bash
# 快速测试
python quick_test.py

# Excel处理测试
python test_excel_processing.py

# 代码执行测试
python test_code_execution.py

# 完整后端测试
python test_backend.py
```

## 📋 测试内容

### 快速测试 (`quick_test.py`)
- ✅ 后端服务状态检查
- ✅ 文件上传功能
- ✅ 文件列表获取
- ✅ 文件详情获取

### Excel处理测试 (`test_excel_processing.py`)
- ✅ Excel文件预处理
- ✅ 无关行识别
- ✅ 合并单元格处理
- ✅ 多级表头处理
- ✅ 数据清理和标准化
- ✅ 元数据生成
- ✅ Elasticsearch索引
- ✅ 文件检索功能

### 代码执行测试 (`test_code_execution.py`)
- ✅ Python代码生成
- ✅ 代码安全执行
- ✅ 数据分析功能
- ✅ 图表生成
- ✅ 复杂分析场景

### 完整后端测试 (`test_backend.py`)
- ✅ 环境配置检查
- ✅ Elasticsearch连接
- ✅ OpenAI连接
- ✅ Excel预处理
- ✅ 元数据生成
- ✅ 文件检索
- ✅ 代码生成
- ✅ 代码执行
- ✅ API端点
- ✅ 完整工作流程

## 🔧 测试环境要求

### 必需服务
1. **后端服务**: 运行在 http://localhost:8000
2. **Elasticsearch**: 运行在 http://localhost:9200
3. **OpenAI API**: 配置有效的API密钥

### 测试数据
- 使用 `data/original/` 目录中的Excel文件
- 自动生成测试CSV数据
- 创建临时测试文件

## 📊 测试结果示例

```
🚀 Excel智能分析系统 - 完整测试套件
============================================================
1. 检查后端服务状态...
✅ 后端服务运行正常

============================================================
🧪 快速功能测试
============================================================
1. 检查后端服务...
   ✅ 后端服务运行正常
2. 测试文件上传...
   ✅ 文件上传成功: cola.xlsx
3. 测试文件列表...
   ✅ 文件列表获取成功: 1 个文件
4. 测试文件详情...
   ✅ 文件详情获取成功: cola.xlsx

🎉 快速测试完成！
============================================================

📊 测试结果汇总
============================================================
快速功能测试                : ✅ 通过
Excel处理功能测试           : ✅ 通过
代码生成和执行测试          : ✅ 通过
完整后端功能测试            : ✅ 通过
------------------------------------------------------------
总计: 4/4 个测试通过
🎉 所有测试通过！系统功能完整！
============================================================
```

## 🐛 故障排除

### 常见问题

1. **后端服务未运行**
   ```
   ❌ 后端服务未运行！
   请先启动后端服务:
   cd week6_hw
   python -c "from backend.main import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8000)"
   ```

2. **Elasticsearch连接失败**
   ```
   ❌ Elasticsearch连接失败: Connection refused
   请确保Elasticsearch运行在 http://localhost:9200
   ```

3. **OpenAI API错误**
   ```
   ❌ OpenAI连接失败: Invalid API key
   请检查 .env 文件中的 OPENAI_API_KEY
   ```

4. **文件上传失败**
   ```
   ❌ 文件上传失败: HTTP 500
   检查后端日志查看详细错误信息
   ```

### 调试技巧

1. **查看详细错误**
   ```bash
   python test_backend.py 2>&1 | tee test_output.log
   ```

2. **单独测试某个功能**
   ```bash
   python -c "
   import asyncio
   from test.test_excel_processing import test_excel_processing
   asyncio.run(test_excel_processing())
   "
   ```

3. **检查测试数据**
   ```bash
   ls -la data/original/
   ls -la data/processed/
   ls -la data/output/
   ```

## 📈 性能基准

### 预期性能指标

| 功能 | 预期时间 | 说明 |
|------|----------|------|
| 文件上传 | < 5秒 | 小文件(< 1MB) |
| Excel预处理 | < 30秒 | 中等文件(1-10MB) |
| 元数据生成 | < 1分钟 | 包含AI处理 |
| 代码生成 | < 10秒 | GPT-4响应 |
| 代码执行 | < 60秒 | 包含图表生成 |

### 资源使用

- **内存**: 建议至少2GB可用内存
- **磁盘**: 测试文件约100MB
- **网络**: 需要稳定的OpenAI API连接

## 🔄 持续集成

### 自动化测试

```bash
#!/bin/bash
# 启动服务
cd week6_hw
python -c "from backend.main import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8000)" &
BACKEND_PID=$!

# 等待服务启动
sleep 10

# 运行测试
cd test
python run_all_tests.py
TEST_RESULT=$?

# 清理
kill $BACKEND_PID
exit $TEST_RESULT
```

## 📝 测试报告

测试完成后会生成详细的测试报告，包括：
- 每个测试的执行状态
- 错误信息和堆栈跟踪
- 性能指标
- 建议改进点

---

**测试套件已准备就绪！** 🎉 开始验证系统功能吧！
