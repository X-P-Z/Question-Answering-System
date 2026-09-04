# ======================
# 2. OpenSearch 客户端初始化
# ======================
from opensearchpy import helpers, OpenSearch
from core.document_core import load_split_files
from core.local_model_core import get_local_model

def init_opensearch_client():
    """连接 OpenSearch 服务（支持本地/云服务）"""
    from dotenv import load_dotenv
    load_dotenv()  # 加载 .env 文件中的配置（可选）
    return OpenSearch(
        hosts=[{"host": "localhost", "port": 9200}],
        http_compress=True,
        use_ssl=False,  # 生产环境建议开启 SSL
        verify_certs=False,
        timeout=30
    )
# ======================
# 3. 创建 OpenSearch 索引（支持向量+BM25检索）
# ======================
def create_opensearch_index(client: OpenSearch, index_name="local_rag_docs", embedding_dim=768):
    """创建支持 KNN 向量检索 + BM25 稀疏检索的索引"""
    index_settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "knn": True,  # 启用向量检索
            "analysis": {  # 配置BM25所需的中文分词器
                "analyzer": {
                    "ik_max_word": {
                        "type": "custom",
                        "tokenizer": "ik_max_word"
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "text": {  # 文本内容（支持BM25检索）
                    "type": "text",
                    "analyzer": "ik_max_word"  # 中文分词
                },
                "metadata": {  # 文档元数据（如文件路径）
                    "type": "object"
                },
                "embedding": {  # 向量字段（支持KNN检索）
                    "type": "knn_vector",
                    "dimension": embedding_dim,
                    "method": {
                        "name": "hnsw",
                        "space_type": "cosinesimil",
                        "parameters": {"ef_construction": 128, "m": 16}
                    }
                }
            }
        }
    }
    if not client.indices.exists(index=index_name):
        client.indices.create(index=index_name, body=index_settings)
        print(f"索引 {index_name} 创建成功（支持向量+BM25检索）")
    else:
        print(f"索引 {index_name} 已存在")


# ======================
# 4. 批量写入 OpenSearch
# ======================
def bulk_write_to_opensearch(client: OpenSearch, docs, embeddings, index_name="local_rag_docs"):
    """将文档和向量批量写入 OpenSearch"""
    actions = []
    for idx, (doc, embedding) in enumerate(zip(docs, embeddings)):
        # 构造元数据（保留文件路径等信息）
        metadata = {
            "file_path": doc.metadata.get("source", ""),
            "chunk_idx": idx,
            "total_chunks": len(docs)
        }
        # 构造批量写入动作
        actions.append({
            "_index": index_name,
            "_id": f"doc_{idx}",  # 自定义文档 ID（可替换为 UUID）
            "_source": {
                "text": doc.page_content,
                "metadata": metadata,
                "embedding": embedding
            }
        })
    # 执行批量写入
    if actions:
        success, failed = helpers.bulk(client, actions)
        print(f"成功写入 {success} 条文档，失败 {failed} 条")
    else:
        print("无文档可写入")

