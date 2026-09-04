import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

_model_cache = None
_streaming_cache = None


def init_model(streaming: bool = False):
    global _model_cache, _streaming_cache
    if _model_cache is not None and _streaming_cache == streaming:
        return _model_cache

    load_dotenv(override=True)
    key = os.getenv("API_KEY")
    _model_cache = ChatOpenAI(
        api_key=key,
        base_url="https://api.deepseek.com",
        model="deepseek-v4-flash",
        temperature=0.9,
        streaming=streaming,
    )
    _streaming_cache = streaming
    return _model_cache