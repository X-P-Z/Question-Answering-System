from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def load_split_files() ->list[Document]:
    # 2. 加载并拆分文档
    loader = DirectoryLoader(
        r"D:\PythonProject\RAG\data",
        glob="*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )
    documents = loader.load()
    print(f"共加载 {len(documents)} 个文档")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", "。", "！", "？", "，", "、"]
    )
    docs = text_splitter.split_documents(documents)
    print(f"文档拆分后共 {len(docs)} 个文本块")
    return docs

