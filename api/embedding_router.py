from fastapi import APIRouter

from core.Opensearch_core import init_opensearch_client, create_opensearch_index, bulk_write_to_opensearch
from core.document_core import load_split_files
from core.local_model_core import get_local_model

embedding_router = APIRouter(
    prefix="/embedding",  # 该模块所有路由的前缀
    tags=["向量模块"],  # 接口文档中的向量标签
    responses={404: {"description": "Not found"}},  # 通用响应
)


#文档批量向量化
@embedding_router.get("/embedding_files")
def get_embedding_files():
#加载目录并拆分
    docs = load_split_files()
#批量向量化
    local_embedding = get_local_model()
    doc_text = [doc.page_content for doc in docs]
    local_embeddings = local_embedding.embed_documents(doc_text)
#链接opensearch
    os_client = init_opensearch_client()
#创建索引
    create_opensearch_index(os_client)
#批量向量化并写入opensearch
    bulk_write_to_opensearch(os_client, docs, local_embeddings)
    return {"message": "向量化完成"}




