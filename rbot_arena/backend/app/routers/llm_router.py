import os
import httpx
from fastapi import APIRouter, HTTPException
from app.core.bus import bus_publish

router = APIRouter(prefix="/llm", tags=["llm"])

def llm_target():
    """Determine LLM endpoint based on provider"""
    prov = os.getenv("LLM_PROVIDER", "rick")
    if prov == "rick":
        return os.getenv("RICK_BASE_URL", "http://127.0.0.1:8000/v1"), None
    if prov == "openai":
        return "https://api.openai.com/v1", os.getenv("OPENAI_API_KEY", "")
    if prov == "router":
        # Optional: custom router for GPT/Grok/Deepseek/GitHub
        return os.getenv("ROUTER_BASE", "http://127.0.0.1:7000/v1"), os.getenv("ROUTER_KEY", "")
    return os.getenv("RICK_BASE_URL", "http://127.0.0.1:8000/v1"), None

@router.post("/chat")
async def chat(body: dict):
    """
    Chat with LLM (Rick local or OpenAI)
    Supports charter-prepended prompts for agents
    """
    base, key = llm_target()
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    
    payload = {
        "model": body.get("model") or os.getenv("RICK_MODEL", "rick-13b-instruct"),
        "messages": body.get("messages", []),
        "stream": False
    }
    
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.post(f"{base}/chat/completions", json=payload, headers=headers)
        if r.status_code >= 400:
            raise HTTPException(r.status_code, r.text)
        js = r.json()
    
    # Publish to event bus
    await bus_publish({
        "source": "llm",
        "type": "explanation",
        "payload": {"model": payload["model"], "snippet": js}
    })
    
    return js
