from sentence_transformers import SentenceTransformer
import torch


class LocalBGEEmbeddings:
    """自定义本地 BGE Embedding 类，适配 LangChain 接口"""

    def __init__(self, device="cpu"):
        self.model = SentenceTransformer(
            model_name_or_path=r"D:\PythonProject\study\demo\day03\local_models\models--BAAI--bge-base-zh-v1.5\snapshots\f03589ceff5aac7111bd60cfc7d497ca17ecac65",
            device=device
        )
        self.query_prefix = "为这个句子生成表示以用于检索相关文档："

    def embed_query(self, text):
        """生成查询向量（带BGE前缀）"""
        text = text.strip()
        embeddings = self.model.encode(
            self.query_prefix + text,
            normalize_embeddings=True,
            batch_size=1,
            show_progress_bar=False
        )
        return embeddings.tolist()

    def embed_documents(self, texts, batch_size=32):
        """批量生成文档向量"""
        texts = [text.strip() for text in texts if text.strip()]
        if not texts:
            return []
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        return embeddings.tolist()

def get_local_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    local_embeddings = LocalBGEEmbeddings(device=device)
    print(f"模型加载完成，运行设备：{device}")
    return local_embeddings

