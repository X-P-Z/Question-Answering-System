# 初始化 Router
import os

from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel

from core.rag_core import upload_document

document_router = APIRouter(
    prefix="/document",
    tags=["文档处理模块"],
    responses={404: {"description": "Not found"}},
)


# 定义响应模型
class DocumentResponse(BaseModel):
    code: int = 200
    msg: str = "success"
    data: bool = True


# 文档上传接口（模拟）
@document_router.post("/upload", response_model=DocumentResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    文档上传接口
    :param file: 上传的文件（txt/docx 等）
    """
    # 实际项目中：保存文件 → 调用 upload_document 生成向量
    save_dir = r"D:\PythonProject\RAG\data"
    os.makedirs(save_dir,exist_ok=True)
    print(file.filename)
    save_path = os.path.join(save_dir,file.filename)
    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)

    success = upload_document(save_path)
    return DocumentResponse(data=success)


# 文档列表接口（模拟）
@document_router.get("/list", response_model=DocumentResponse)
def get_document_list():
    """获取已上传的文档列表"""
    return DocumentResponse(data=True, msg="文档列表获取成功")