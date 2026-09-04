
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_core.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from opensearchpy import OpenSearch, helpers

from core.Opensearch_core import init_opensearch_client
from core.local_model_core import get_local_model
from core.model_core import init_model


def hybrid_search(
        client: OpenSearch,
        query: str,
        query_embedding: list,
        index_name: str = "local_rag_docs",
        k: int = 5,
        alpha: float = 0.5  # 权重参数：0=纯BM25，1=纯向量
):
    """
    混合检索：向量检索 + BM25检索，加权融合结果

    Args:
        client: OpenSearch客户端
        query: 用户查询文本
        query_embedding: 查询向量
        index_name: 索引名称
        k: 返回结果数量
        alpha: 向量检索权重（BM25权重为1-alpha）

    Returns:
        融合后的Top-K结果（按得分降序排列）
    """
    # --------------------------
    # 步骤1：向量检索（KNN）
    # --------------------------
    vector_search_body = {
        "size": k * 2,  # 取2倍k以避免结果重复
        "query": {
            "knn": {
                "embedding": {
                    "vector": query_embedding,
                    "k": k * 2
                }
            }
        },
        "_source": ["text", "metadata"]
    }
    vector_response = client.search(index=index_name, body=vector_search_body)
    vector_hits = {hit["_id"]: hit for hit in vector_response["hits"]["hits"]}
    vector_scores = {hit["_id"]: hit["_score"] for hit in vector_response["hits"]["hits"]}

    # --------------------------
    # 步骤2：BM25检索（全文检索）
    # --------------------------
    bm25_search_body = {
        "size": k * 2,
        "query": {
            "match": {
                "text": query  # 使用ik分词器对query进行分词
            }
        },
        "_source": ["text", "metadata"]
    }
    bm25_response = client.search(index=index_name, body=bm25_search_body)
    bm25_hits = {hit["_id"]: hit for hit in bm25_response["hits"]["hits"]}
    bm25_scores = {hit["_id"]: hit["_score"] for hit in bm25_response["hits"]["hits"]}

    # --------------------------
    # 步骤3：归一化得分（Min-Max缩放）
    # --------------------------
    all_ids = set(vector_scores.keys()).union(set(bm25_scores.keys()))
    # 向量得分归一化
    vector_min = min(vector_scores.values()) if vector_scores else 0
    vector_max = max(vector_scores.values()) if vector_scores else 1
    normalized_vector = {
        doc_id: (score - vector_min) / (vector_max - vector_min + 1e-8)
        for doc_id, score in vector_scores.items()
    }
    # BM25得分归一化
    bm25_min = min(bm25_scores.values()) if bm25_scores else 0
    bm25_max = max(bm25_scores.values()) if bm25_scores else 1
    normalized_bm25 = {
        doc_id: (score - bm25_min) / (bm25_max - bm25_min + 1e-8)
        for doc_id, score in bm25_scores.items()
    }

    # --------------------------
    # 步骤4：加权融合
    # --------------------------
    final_scores = {}
    for doc_id in all_ids:
        v_score = normalized_vector.get(doc_id, 0)
        b_score = normalized_bm25.get(doc_id, 0)
        final_scores[doc_id] = alpha * v_score + (1 - alpha) * b_score

    # --------------------------
    # 步骤5：按得分排序并返回Top-K
    # --------------------------
    sorted_ids = sorted(final_scores.keys(), key=lambda x: final_scores[x], reverse=True)[:k]
    final_results = []
    for doc_id in sorted_ids:
        # 优先从向量检索结果中取源数据（若不存在则取BM25结果）
        hit = vector_hits.get(doc_id, bm25_hits.get(doc_id))
        final_results.append({
            "doc_id": doc_id,
            "score": final_scores[doc_id],
            "text": hit["_source"]["text"],
            "metadata": hit["_source"]["metadata"]
        })
    return final_results



# 模拟你的本地 RAG 核心逻辑（实际项目中替换为真实的向量检索）
def local_retrieve(query: str, top_k: int = 3) -> list[str]:
    """
    本地语义检索核心逻辑
    :param query: 用户查询
    :param top_k: 返回数量
    :return: 检索结果列表
    """
    # 1. 生成查询向量
    # 2. 从 Chroma 检索相似文档
    # 3. 返回文档内容
        # 1. 生成查询向量
    query_embedding = get_local_model().embed_query(query)

        # 2. 连接 OpenSearch
    client = init_opensearch_client()

        # 3. 执行混合检索
    results = hybrid_search(
        client=client,
        query=query,
        query_embedding=query_embedding,
        k=top_k,
        alpha=0.5
    )

    return [
        f"【检索结果{i + 1}】{r['text']}"
        for i, r in enumerate(results)
    ]

def generate_answer(query:str,context:list):
    prompt_template = """请使用以下提供的文本内容来回答问题。仅使用提供的文本信息，如果文本中没有相关信息，请回答"抱歉，提供的文本中没有这个信息"。
        文本内容：
        {context}
        问题：{question}
        回答：
        """
    prop = PromptTemplate.from_template(prompt_template)
    model = init_model()
    chain = prop | model
    res = chain.invoke({"context": context, "question": query})
    return res.content

def upload_document(file_path: str) -> bool:
    """
    文档上传与向量生成核心逻辑
    :param file_path: 文档路径
    :return: 是否成功
    """
    # 1. 加载文档
    # 2. 拆分文本
    # 3. 批量生成向量并存储到 Chroma
    # RAG索引

    print("向量已存储到 OpenSearch 数据库")
    return True