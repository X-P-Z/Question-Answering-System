from fastapi import APIRouter
from pydantic import BaseModel

from core.rag_core import local_retrieve, generate_answer

# 1. 初始化 Router 实例（指定前缀和标签，方便文档分类）
retrieve_router = APIRouter(
    prefix="/retrieve",  # 该模块所有路由的前缀
    tags=["检索模块"],  # 接口文档中的分类标签
    responses={404: {"description": "Not found"}},  # 通用响应
)


# 2. 定义请求模型
class RetrieveRequest(BaseModel):
    query: str
    top_k: int = 3


class RetrieveResponse(BaseModel):
    answer: str
    sources: list[str]


@retrieve_router.get("/search", response_model=RetrieveResponse)
def retrieve_get(query: str, top_k: int = 3):
    """GET 方式检索"""
    results = local_retrieve(query, top_k)
    answer = generate_answer(query,results)
    return {"answer": answer, "sources": results}
