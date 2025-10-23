# PowerShell脚本：创建.env配置文件
# 用法：.\create_env.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Excel智能分析系统 - 环境配置" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查.env是否已存在
if (Test-Path ".env") {
    Write-Host "⚠️  .env文件已存在" -ForegroundColor Yellow
    $overwrite = Read-Host "是否覆盖? (y/N)"
    if ($overwrite -ne "y" -and $overwrite -ne "Y") {
        Write-Host "取消操作" -ForegroundColor Red
        exit
    }
}

# 获取OpenAI API Key
Write-Host "请输入您的OpenAI API Key:" -ForegroundColor Green
Write-Host "(格式: sk-...)" -ForegroundColor Gray
$apiKey = Read-Host "API Key"

if ([string]::IsNullOrWhiteSpace($apiKey)) {
    Write-Host "❌ API Key不能为空" -ForegroundColor Red
    exit
}

# 创建.env文件内容
$envContent = @"
# OpenAI配置
OPENAI_API_KEY=$apiKey

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
"@

# 写入文件
$envContent | Out-File -FilePath ".env" -Encoding utf8 -NoNewline

Write-Host ""
Write-Host "✅ .env文件创建成功！" -ForegroundColor Green
Write-Host ""
Write-Host "下一步：" -ForegroundColor Cyan
Write-Host "1. 启动Elasticsearch: docker run -d --name elasticsearch -p 9200:9200 -e `"discovery.type=single-node`" -e `"xpack.security.enabled=false`" docker.elastic.co/elasticsearch/elasticsearch:8.10.0" -ForegroundColor Gray
Write-Host "2. 初始化索引: cd backend && python scripts/init_es_index.py" -ForegroundColor Gray
Write-Host "3. 启动后端: cd backend && python main.py" -ForegroundColor Gray
Write-Host "4. 启动前端: cd frontend && npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "详细说明请查看 SETUP_COMPLETE.md" -ForegroundColor Yellow

