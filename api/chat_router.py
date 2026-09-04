import json
import uuid
import os

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool

from core.model_core import init_model
from core.rag_core import local_retrieve
from core.session_core import create_session, get_history, add_message, clear_session, get_active_count

chat_router = APIRouter(
    prefix="/chat",
    tags=["对话模块"],
    responses={404: {"description": "Not found"}},
)


class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str
    enable_rag: bool = True
    top_k: int = 3


class ClearRequest(BaseModel):
    session_id: str


# === Tools for Agent ===

@tool
def search_documents(query: str, top_k: int = 3) -> str:
    """Search the local document knowledge base for relevant information.
    Use this when the user asks about information contained in uploaded documents or the knowledge base."""
    return "\n\n".join(_safe_retrieve(query, top_k))


@tool
def list_documents() -> str:
    """List all available documents in the knowledge base."""
    data_dir = r"D:\PythonProject\RAG\data"
    if not os.path.exists(data_dir):
        return "No documents available."
    files = [f for f in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, f))]
    return "\n".join(files) if files else "No documents available."


TOOLS = [search_documents, list_documents]
TOOL_MAP = {t.name: t for t in TOOLS}


def _safe_retrieve(query: str, top_k: int) -> list[str]:
    try:
        return local_retrieve(query, top_k)
    except Exception as e:
        return [f"[RAG unavailable: OpenSearch connection failed. Answering without document retrieval. Error: {e}]"]


# === Streaming Generator ===

async def _stream_generator(session_id: str | None, message: str, enable_rag: bool, top_k: int):
    try:
        if not session_id:
            session_id = create_session()
        else:
            history = get_history(session_id)
            if not history:
                create_session()

        # Build system prompt
        system_content = "You are a helpful AI assistant. Answer questions clearly and concisely."

        context = []
        if enable_rag:
            context = _safe_retrieve(message, top_k)
            context_text = "\n\n".join(context)
            system_content += f"\n\nUse the following retrieved context to answer the question:\n{context_text}"

        messages = [SystemMessage(content=system_content)]
        messages.extend(get_history(session_id))
        messages.append(HumanMessage(content=message))

        model = init_model(streaming=True)
        full_response = ""

        async for chunk in model.astream(messages):
            if chunk.content:
                full_response += chunk.content
                yield f"data: {json.dumps({'type': 'token', 'content': chunk.content}, ensure_ascii=False)}\n\n"

        add_message(session_id, "user", message)
        add_message(session_id, "assistant", full_response)

        if enable_rag:
            sources = context
            yield f"data: {json.dumps({'type': 'sources', 'sources': sources}, ensure_ascii=False)}\n\n"

        yield f"data: {json.dumps({'type': 'done', 'session_id': session_id})}\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"


# === Agent Streaming Generator ===

async def _agent_generator(session_id: str | None, message: str, enable_rag: bool, top_k: int):
    try:
        if not session_id:
            session_id = create_session()
        else:
            history = get_history(session_id)
            if not history:
                create_session()

        system_content = (
            "You are an intelligent AI assistant with access to tools. "
            "Use the tools to search the document knowledge base when needed. "
            "If the user asks about information in documents, always use search_documents first. "
            "Answer in a clear and concise manner."
        )

        messages = [SystemMessage(content=system_content)]
        messages.extend(get_history(session_id))
        messages.append(HumanMessage(content=message))

        model = init_model(streaming=True)
        model_with_tools = model.bind_tools(TOOLS)

        full_response = ""

        for _ in range(5):
            response = await model_with_tools.ainvoke(messages)

            if response.tool_calls:
                messages.append(response)
                for tc in response.tool_calls:
                    tool_name = tc.get("name", "")
                    tool_args = tc.get("args", {})
                    yield f"data: {json.dumps({'type': 'tool_call', 'name': tool_name, 'args': tool_args}, ensure_ascii=False)}\n\n"

                    if tool_name in TOOL_MAP:
                        if tool_name == "search_documents" and not enable_rag:
                            result = "RAG search is disabled."
                        else:
                            result = TOOL_MAP[tool_name].invoke(tool_args)
                    else:
                        result = f"Unknown tool: {tool_name}"

                    yield f"data: {json.dumps({'type': 'tool_result', 'name': tool_name, 'result': result}, ensure_ascii=False)}\n\n"
                    messages.append(ToolMessage(content=str(result), tool_call_id=tc.get("id", "")))
            else:
                # Stream the final response
                async for chunk in model.astream(messages):
                    if chunk.content:
                        full_response += chunk.content
                        yield f"data: {json.dumps({'type': 'token', 'content': chunk.content}, ensure_ascii=False)}\n\n"
                break

        add_message(session_id, "user", message)
        add_message(session_id, "assistant", full_response)
        yield f"data: {json.dumps({'type': 'done', 'session_id': session_id})}\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"


# === Endpoints ===

@chat_router.post("/stream")
async def chat_stream(req: ChatRequest):
    return StreamingResponse(
        _stream_generator(req.session_id, req.message, req.enable_rag, req.top_k),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@chat_router.post("/agent")
async def chat_agent(req: ChatRequest):
    return StreamingResponse(
        _agent_generator(req.session_id, req.message, req.enable_rag, req.top_k),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@chat_router.post("/clear")
def chat_clear(req: ClearRequest):
    clear_session(req.session_id)
    return {"success": True}


@chat_router.get("/sessions")
def chat_sessions():
    return {"active_sessions": get_active_count()}