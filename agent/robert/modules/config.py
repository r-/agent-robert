"""Config module — manages agent settings and security flags."""

__all__ = ["AgentConfig", "load_config"]

# ─── API (public contract) ───────────────────────────

from dataclasses import dataclass, field
import json
import os

@dataclass
class ToolConfig:
    enabled: bool = False
    allowlist: list[str] = field(default_factory=list)

@dataclass
class AgentConfig:
    provider: str = "openrouter"
    model: str = "google/gemini-2.0-flash-001"
    restrict_to_workspace: bool = True
    tools: dict[str, ToolConfig] = field(default_factory=lambda: {
        "shell": ToolConfig(),
        "fileWrite": ToolConfig(),
        "spawn": ToolConfig(),
        "cron": ToolConfig(),
        "mcp": ToolConfig(),
        "homeassistant": ToolConfig(),
    })

def load_config(path: str = "config.json") -> AgentConfig:
    """Load config from JSON or return defaults."""
    if not os.path.exists(path):
        return AgentConfig()
    
    with open(path, "r") as f:
        data = json.load(f)
    
    # Parse tool configs from JSON
    tools = AgentConfig().tools  # start with defaults (all disabled)
    raw_tools = data.get("tools", {})
    for name, raw in raw_tools.items():
        if isinstance(raw, dict):
            tools[name] = ToolConfig(
                enabled=raw.get("enabled", False),
                allowlist=raw.get("allowlist", []),
            )

    return AgentConfig(
        provider=data.get("provider", "openrouter"),
        model=data.get("model", "google/gemini-2.0-flash-001"),
        restrict_to_workspace=data.get("restrictToWorkspace", True),
        tools=tools,
    )

# ─── INTERNAL (private) ──

# (Any secret resolution logic)
