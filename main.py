# 初始化应用
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.chat_router import chat_router
from api.document_router import document_router
from api.embedding_router import embedding_router
from api.retrieve_router import retrieve_router

app = FastAPI(
    title="私有化 RAG 接口服务",
    description="基于 FastAPI + 本地 BGE + Chroma 的 RAG 接口",
    version="1.0.0"
)

# 核心：注册模块化路由
app.include_router(chat_router)  # 注册对话模块（流式+智能体）
app.include_router(retrieve_router)  # 注册检索模块
app.include_router(document_router)  # 注册文档处理模块
app.include_router(embedding_router)  # 注册向量模块

# ======================
# 3. 配置 CORS 中间件（核心：解决前端跨域）
# ======================
app.add_middleware(
    CORSMiddleware,
    # 允许跨域的源：生产环境建议指定具体域名（如 ["https://your-frontend.com"]）
    allow_origins=["*"],  # 开发环境用*，生产环境替换为具体域名
    # 允许跨域携带 Cookie（前端需要传 Cookie 时开启）
    allow_credentials=True,
    # 允许的 HTTP 方法：GET/POST/PUT/DELETE 等
    allow_methods=["*"],  # 开发环境用*，生产环境可指定 ["GET", "POST"]
    # 允许的 HTTP 请求头：如 Content-Type/Authorization 等
    allow_headers=["*"],  # 开发环境用*，生产环境可指定具体头
    # 暴露给前端的响应头（前端需要读取的自定义头）
    expose_headers=["X-Total-Count"],
    # 预检请求的缓存时间（秒）：减少 OPTIONS 请求次数，提升性能
    max_age=3600
)


# 根路由
@app.get("/")
def root():
    return {"message": "私有化 RAG 接口服务启动成功"}

# 启动命令：uvicorn main:app --reload --host 0.0.0.0 --port 8000



