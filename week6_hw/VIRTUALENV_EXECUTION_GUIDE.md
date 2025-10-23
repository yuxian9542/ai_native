# 🐍 虚拟环境代码执行系统指南

## 概述
Excel智能分析系统支持在虚拟环境中执行Python代码，这是比Docker更简单、更可靠的解决方案。

## 🏗️ 架构设计

### 执行环境
- **Python环境**: 与后端相同的虚拟环境
- **预装包**: pandas, numpy, matplotlib, openpyxl
- **安全措施**: 代码安全检查，临时目录隔离
- **超时控制**: 60秒执行超时

### 核心组件
- `virtualenv_code_executor.py`: 虚拟环境代码执行器
- `unified_code_executor.py`: 统一执行器
- `code_executor.py`: 本地执行器（备用）

## 🚀 使用方法

### 1. 自动执行
系统会自动选择最佳执行环境：
1. 优先使用虚拟环境执行
2. 失败时回退到本地执行
3. 记录详细的执行日志

### 2. 手动测试
```bash
cd test
python test_virtualenv_execution.py
```

## 🔧 配置选项

### 环境变量
```bash
# .env文件
USE_DOCKER_EXECUTION=false  # 禁用Docker执行
CODE_EXECUTION_TIMEOUT=60   # 执行超时时间
```

### 代码安全检查
- 禁止导入系统模块（os, subprocess, sys）
- 禁止使用危险函数（eval, exec, compile）
- 限制文件操作（只允许读取模式）

## 📊 执行流程

1. **代码生成**: GPT-4生成Python分析代码
2. **安全检查**: 验证代码安全性
3. **环境准备**: 创建临时工作目录
4. **代码执行**: 在虚拟环境中运行
5. **结果收集**: 捕获输出和错误信息
6. **资源清理**: 删除临时文件

## 🛠️ 故障排除

### 常见问题
1. **编码错误**: 系统自动处理UTF-8编码
2. **包缺失**: 确保虚拟环境包含所需包
3. **权限问题**: 检查临时目录权限
4. **超时问题**: 调整CODE_EXECUTION_TIMEOUT

### 调试方法
```bash
# 查看执行日志
tail -f backend/logs/excel_analysis_*.log

# 测试环境
python -c "import pandas, numpy, matplotlib; print('环境正常')"
```

## 📈 性能优化

### 执行速度
- 虚拟环境启动快
- 包已预装，无需下载
- 内存占用低

### 稳定性
- 与后端环境一致
- 避免Docker复杂性
- 错误处理完善

## 🎯 优势

1. **简单**: 无需Docker配置
2. **快速**: 执行速度快
3. **可靠**: 环境一致性好
4. **易调试**: 错误信息清晰
5. **资源友好**: 内存占用低

虚拟环境执行是推荐的生产环境解决方案！