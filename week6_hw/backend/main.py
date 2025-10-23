"""
FastAPI主应用入口
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.api.rest import router as rest_router
from backend.api.websocket import handle_websocket
from backend.utils.es_client import es_client
from backend.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print("=" * 50)
    print("Excel智能分析系统启动中...")
    print(f"后端服务: http://{settings.backend_host}:{settings.backend_port}")
    print(f"API文档: http://{settings.backend_host}:{settings.backend_port}/docs")
    print(f"Elasticsearch: {settings.elasticsearch_url}")
    print("=" * 50)
    
    # 检查ES连接
    es_connected = await es_client.ping()
    if es_connected:
        print("✓ Elasticsearch连接成功")
    else:
        print("✗ Elasticsearch连接失败，请检查配置")
    
    yield
    
    # 关闭时
    await es_client.close()
    print("应用已关闭")


# 创建FastAPI应用
app = FastAPI(
    title="Excel智能分析系统",
    description="基于AI的Excel数据分析平台",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册REST API路由
app.include_router(rest_router, prefix="/api", tags=["API"])


# WebSocket端点
@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket聊天端点"""
    await handle_websocket(websocket)


# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Excel智能分析系统",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True
    )

