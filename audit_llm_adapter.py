"""
LLM 适配层 (C-1): OpenAI 兼容接口封装

支持: 阿里云 DashScope (通义千问), DeepSeek, 火山方舟(豆包), Flow2API 等

配置 (从 .llm_secret 或环境变量读):
  LLM_BASE_URL    OpenAI 兼容 endpoint (默认阿里云 DashScope)
  LLM_API_KEY     API key
  LLM_MODEL_TEXT  文本审核默认模型 (如 qwen-plus)
  LLM_MODEL_VISION 视觉默认模型 (如 qwen-vl-plus)
  LLM_MODEL_EMBED 嵌入默认模型 (如 text-embedding-v3)

提供:
  get_client() → openai.OpenAI
  chat_json(system, user, model=None, temperature=0) → dict (期望返回 JSON)
  chat_text(system, user, model=None, temperature=0) → str
  vision_chat(system, user_text, image_urls, model=None) → str
  embeddings(texts, model=None) → List[List[float]]
"""
import json
import os
import re
from pathlib import Path
from typing import List, Optional


def _load_secret():
    """从 .llm_secret 或环境变量加载配置"""
    conf = {}
    secret_file = Path(__file__).parent / ".llm_secret"
    if secret_file.exists():
        for line in secret_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                conf[k.strip()] = v.strip()
    # 环境变量覆盖
    for k in ("LLM_BASE_URL", "LLM_API_KEY",
              "LLM_MODEL_TEXT", "LLM_MODEL_VISION", "LLM_MODEL_EMBED"):
        env = os.environ.get(k)
        if env:
            conf[k] = env
    return conf


_CONF = _load_secret()
_client = None
_async_client = None


def get_client():
    """返回单例同步 OpenAI 客户端"""
    global _client
    if _client is None:
        from openai import OpenAI
        base_url = _CONF.get("LLM_BASE_URL")
        api_key = _CONF.get("LLM_API_KEY")
        if not api_key:
            raise RuntimeError("LLM_API_KEY 未配置 (.llm_secret 或环境变量)")
        _client = OpenAI(base_url=base_url, api_key=api_key)
    return _client


def get_async_client():
    """返回单例异步 OpenAI 客户端 (支持 100+ 并发连接)"""
    global _async_client
    if _async_client is None:
        from openai import AsyncOpenAI
        import httpx
        base_url = _CONF.get("LLM_BASE_URL")
        api_key = _CONF.get("LLM_API_KEY")
        if not api_key:
            raise RuntimeError("LLM_API_KEY 未配置")
        # httpx 连接池提高 limits 支持高并发 (500 足够应对 300+ 并发)
        limits = httpx.Limits(max_connections=500, max_keepalive_connections=300)
        http_client = httpx.AsyncClient(limits=limits, timeout=httpx.Timeout(120.0))
        _async_client = AsyncOpenAI(base_url=base_url, api_key=api_key, http_client=http_client)
    return _async_client


def model_text():
    return _CONF.get("LLM_MODEL_TEXT") or "qwen-plus"


def model_vision():
    return _CONF.get("LLM_MODEL_VISION") or "qwen-vl-plus"


def model_embed():
    return _CONF.get("LLM_MODEL_EMBED") or "text-embedding-v3"


def chat_text(system: str, user: str, model: Optional[str] = None,
              temperature: float = 0.0, max_tokens: int = 2000) -> str:
    client = get_client()
    resp = client.chat.completions.create(
        model=model or model_text(),
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content or ""


_JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)


def _extract_json(s: str) -> dict:
    """从模型输出中抽 JSON (容忍 ```json``` 包裹 / 前后文字)"""
    if not s:
        return {}
    s = s.strip()
    # 1) ```json ... ``` 块
    m = _JSON_BLOCK_RE.search(s)
    if m:
        s = m.group(1)
    # 2) 取第一个 { 到最后一个 }
    start = s.find("{")
    end = s.rfind("}")
    if start < 0 or end <= start:
        return {"_raw": s}
    candidate = s[start:end + 1]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        # 尝试更宽松的解析: 把裸引号替换、处理尾逗号
        fixed = re.sub(r",(\s*[}\]])", r"\1", candidate)
        try:
            return json.loads(fixed)
        except Exception:
            return {"_raw": s, "_parse_error": True}


def chat_json(system: str, user: str, model: Optional[str] = None,
              temperature: float = 0.0, max_tokens: int = 2000) -> dict:
    """对话返回 JSON. 若未命中 JSON 结构则返回 {'_raw': s}"""
    text = chat_text(system, user, model=model, temperature=temperature,
                     max_tokens=max_tokens)
    return _extract_json(text)


async def chat_text_async(system: str, user: str, model: Optional[str] = None,
                          temperature: float = 0.0, max_tokens: int = 2000,
                          max_retries: int = 4) -> str:
    """异步对话, 含指数退避重试"""
    import asyncio as _asyncio
    client = get_async_client()
    for attempt in range(max_retries):
        try:
            resp = await client.chat.completions.create(
                model=model or model_text(),
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return resp.choices[0].message.content or ""
        except Exception as e:
            msg = str(e)
            retryable = any(k in msg for k in ("429", "500", "502", "503", "504", "timeout", "Timeout"))
            if not retryable or attempt == max_retries - 1:
                raise
            await _asyncio.sleep((2 ** attempt) + 0.5 * attempt)
    return ""


async def chat_json_async(system: str, user: str, model: Optional[str] = None,
                          temperature: float = 0.0, max_tokens: int = 2000) -> dict:
    """异步对话返回 JSON"""
    text = await chat_text_async(system, user, model=model, temperature=temperature,
                                  max_tokens=max_tokens)
    return _extract_json(text)


async def vision_chat_async(system: str, user_text: str, image_urls: List[str],
                             model: Optional[str] = None, temperature: float = 0.0,
                             max_tokens: int = 2000, max_retries: int = 4) -> str:
    """异步视觉对话, 含指数退避重试 (应对 429 限流)"""
    import asyncio as _asyncio
    client = get_async_client()
    content = [{"type": "text", "text": user_text}]
    for url in image_urls:
        content.append({"type": "image_url", "image_url": {"url": url}})
    for attempt in range(max_retries):
        try:
            resp = await client.chat.completions.create(
                model=model or model_vision(),
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": content},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return resp.choices[0].message.content or ""
        except Exception as e:
            msg = str(e)
            # 429 / 5xx / 超时 → 退避重试
            retryable = any(k in msg for k in ("429", "500", "502", "503", "504", "timeout", "Timeout"))
            if not retryable or attempt == max_retries - 1:
                raise
            await _asyncio.sleep((2 ** attempt) + 0.5 * attempt)
    return ""


async def vision_json_async(system: str, user_text: str, image_urls: List[str],
                             model: Optional[str] = None, temperature: float = 0.0) -> dict:
    text = await vision_chat_async(system, user_text, image_urls, model=model,
                                     temperature=temperature)
    return _extract_json(text)


def vision_chat(system: str, user_text: str, image_urls: List[str],
                model: Optional[str] = None, temperature: float = 0.0,
                max_tokens: int = 2000) -> str:
    """视觉对话: 传入多张图片 URL + 文本提示"""
    client = get_client()
    # 组装 multi-modal user content
    content = [{"type": "text", "text": user_text}]
    for url in image_urls:
        content.append({"type": "image_url", "image_url": {"url": url}})
    resp = client.chat.completions.create(
        model=model or model_vision(),
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": content},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content or ""


def vision_json(system: str, user_text: str, image_urls: List[str],
                model: Optional[str] = None, temperature: float = 0.0) -> dict:
    text = vision_chat(system, user_text, image_urls, model=model, temperature=temperature)
    return _extract_json(text)


def embeddings(texts: List[str], model: Optional[str] = None) -> List[List[float]]:
    """文本嵌入. 单次最多 25 条 (阿里云限制)."""
    client = get_client()
    model_name = model or model_embed()
    out = []
    batch = 25
    for i in range(0, len(texts), batch):
        resp = client.embeddings.create(model=model_name, input=texts[i:i + batch])
        out.extend([d.embedding for d in resp.data])
    return out


if __name__ == "__main__":
    import sys
    # 烟雾测试
    print(f"配置: base={_CONF.get('LLM_BASE_URL')}, model={model_text()}")
    if not _CONF.get("LLM_API_KEY"):
        print("[ERR] 未配置 LLM_API_KEY")
        sys.exit(1)
    r = chat_json(
        system="你是一个简洁的 JSON 返回助手. 只返回 JSON, 不要其他文字.",
        user="请返回 JSON: {\"status\":\"ok\",\"echo\":\"hello\"}",
    )
    print("测试返回:", r)
