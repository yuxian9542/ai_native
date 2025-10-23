# 🧪 Excel智能分析系统 - 测试套件

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
cd test
python run_all_tests.py
```

### 2. 运行特定测试
```bash
# 快速测试
python quick_test.py

# 后端功能测试
python test_backend.py

# Excel处理测试
python test_excel_processing.py

# 代码执行测试
python test_code_execution.py
```

### 3. 测试环境要求
- Python 3.9+
- 后端服务运行在 localhost:8000
- Elasticsearch运行在 localhost:9200
- OpenAI API Key已配置

## 📊 测试覆盖

### 后端功能
- ✅ 文件上传和处理
- ✅ 元数据生成
- ✅ Elasticsearch索引
- ✅ 文件检索
- ✅ 代码生成
- ✅ 代码执行
- ✅ 文件删除

### 前端功能
- ✅ 文件管理界面
- ✅ 上传功能
- ✅ 删除功能
- ✅ 侧边栏折叠

### 集成测试
- ✅ 端到端工作流
- ✅ 错误处理
- ✅ 性能测试
- ✅ 日志记录

## 🔧 测试配置

### 环境变量
```bash
# .env文件
OPENAI_API_KEY=your_api_key
ELASTICSEARCH_URL=http://localhost:9200
```

### 测试数据
- 测试文件位于 `test/data/` 目录
- 支持多种Excel格式
- 包含复杂表头测试用例

## 📝 测试报告

### 运行测试后查看
- 控制台输出：实时测试结果
- 日志文件：`test/logs/excel_analysis_*.log`
- 测试数据：`test/data/processed/`

### 测试结果示例
```
✅ 测试通过: 文件上传功能
✅ 测试通过: Excel预处理
✅ 测试通过: 元数据生成
✅ 测试通过: 代码执行
❌ 测试失败: 网络连接
```

## 🛠️ 故障排除

### 常见问题
1. **连接错误**: 确保后端和Elasticsearch正在运行
2. **API错误**: 检查OpenAI API Key配置
3. **文件错误**: 确保测试数据文件存在
4. **权限错误**: 检查文件读写权限

### 调试方法
```bash
# 查看详细日志
tail -f test/logs/excel_analysis_*.log

# 运行单个测试
python test_backend.py --verbose

# 检查环境
python -c "import requests; print(requests.get('http://localhost:8000/health').json())"
```

## 📈 性能测试

### 测试指标
- 文件上传速度
- 处理时间
- 代码执行时间
- 内存使用

### 基准测试
```bash
# 性能测试
python test_performance.py

# 压力测试
python test_stress.py
```

测试套件确保系统功能完整性和稳定性！