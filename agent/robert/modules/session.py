"""Session module — handles conversation history persistence via JSONL."""

__all__ = ["Session", "SessionManager"]

# ─── API (public contract) ───────────────────────────

import json
import os
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Message:
    role: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    tool_calls: list = field(default_factory=list)
    tool_call_id: str = ""

class Session:
    def __init__(self, key: str, storage_path: str):
        self.key = key
        self._path = storage_path
        self._messages: list[Message] = []
        self._load()

    def _load(self):
        if not os.path.exists(self._path):
            return
        with open(self._path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    self._messages.append(Message(**data))

    def add_user_message(self, content: str):
        self._append(Message(role="user", content=content))

    def add_user_audio_message(self, content: str):
        # content is "data:audio/wav;base64,....."
        # We store it as content, but the provider must parse it.
        # Alternatively, we could add a `type="audio"` field to Message.
        # For simplicity in Level 1, we'll prefix it.
        self._append(Message(role="user", content=content))

    def add_assistant_message(self, content: str):
        self._append(Message(role="assistant", content=content))

    def add_tool_call_message(self, content: str, tool_calls: list):
        self._append(Message(role="assistant", content=content, tool_calls=tool_calls))

    def add_tool_result_message(self, tool_call_id: str, content: str):
        self._append(Message(role="tool", content=content, tool_call_id=tool_call_id))

    def _append(self, msg: Message):
        self._messages.append(msg)
        with open(self._path, "a", encoding="utf-8") as f:
            # We filter out empty strings/lists to keep JSONL clean
            d = {k: v for k, v in vars(msg).items() if v or k == "content"}
            f.write(json.dumps(d) + "\n")

    def get_messages_for_llm(self, system_prompt: str) -> list[dict]:
        msgs = [{"role": "system", "content": system_prompt}]
        for m in self._messages:
            d = {"role": m.role, "content": m.content}
            if m.tool_calls:
                d["tool_calls"] = m.tool_calls
            if m.tool_call_id:
                d["tool_call_id"] = m.tool_call_id
            msgs.append(d)
        return msgs

class SessionManager:
    def __init__(self, directory: str = "sessions"):
        self._dir = directory
        if not os.path.exists(directory):
            os.makedirs(directory)

    def get_session(self, key: str) -> Session:
        # Sanitize key for filename
        safe_key = "".join(c for c in key if c.isalnum() or c in ("-", "_")).lower()
        path = os.path.join(self._dir, f"{safe_key}.jsonl")
        return Session(key, path)

# ─── INTERNAL (private) ──
