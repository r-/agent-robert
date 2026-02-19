"""Provider module — adapter for LLM services (OpenRouter)."""

__all__ = ["LLMResponse", "ProviderPort", "OpenRouterAdapter"]

# ─── API (public contract) ───────────────────────────

from dataclasses import dataclass, field
from typing import Protocol
import httpx

@dataclass
class LLMResponse:
    content: str
    tool_calls: list = field(default_factory=list)

class ProviderPort(Protocol):
    async def chat(self, messages: list[dict]) -> LLMResponse: ...


class OpenRouterAdapter:
    """Lite-weight adapter for OpenRouter API."""
    def __init__(self, api_key: str, model: str):
        self._api_key = api_key
        self._model = model
        self._url = "https://openrouter.ai/api/v1/chat/completions"

    # (Deleted duplicate method)

    def _format_message(self, msg: dict) -> dict:
        content = msg.get("content", "")
        role = msg.get("role", "user")
        
        # Check for our data URI marker
        if isinstance(content, str) and content.startswith("data:audio/"):
            parts = content.split(",")
            if len(parts) == 2:
                base64_data = parts[1]
                return {
                    "role": role,
                    "content": [
                        {
                            "type": "input_audio",
                            "input_audio": {
                                "data": base64_data,
                                "format": "wav"
                            }
                        },
                        {
                            "type": "text",
                            "text": "This is an audio message from the user."
                        }
                    ]
                }
        return msg

    async def chat(self, messages: list[dict], tools: list[dict] = None) -> LLMResponse:
        """Call OpenRouter with messages."""
        if not self._api_key:
            return LLMResponse(content="Error: Missing OPENROUTER_API_KEY in .env")

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/maker-norr/agent-robert",
            "X-Title": "Agent R.O.B.E.R.T.",
        }
        
        # Transform messages to handle audio
        formatted_messages = [self._format_message(m) for m in messages]
        
        payload = {
            "model": self._model,
            "messages": formatted_messages,
        }
        if tools:
            payload["tools"] = tools

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                r = await client.post(self._url, headers=headers, json=payload)
                r.raise_for_status()
                data = r.json()
                
                choice = data.get("choices", [{}])[0]
                msg = choice.get("message", {})
                content = msg.get("content") or ""
                tool_calls = msg.get("tool_calls") or []
                
                return LLMResponse(content=content, tool_calls=tool_calls)
            except httpx.HTTPStatusError as e:
                return LLMResponse(content=f"LLM Error {e.response.status_code}: {e.response.text}")
            except Exception as e:
                return LLMResponse(content=f"Connection Error: {str(e)}")

# ─── INTERNAL (private) ──
