"""Composition Root — wires modules together."""

import os
from dotenv import load_dotenv

from robert.modules.config import load_config
from robert.modules.session import SessionManager
from robert.modules.providers import OpenRouterAdapter
from robert.modules.agent import AgentService, ContextBuilder
from robert.modules.tools import ToolRegistry

def create_agent_service(config_path: str = "config.json") -> AgentService:
    """Wires up and returns a ready-to-use AgentService."""
    load_dotenv()
    
    # 1. Load config
    cfg = load_config(config_path)
    
    # 2. Initialize modules
    sessions = SessionManager()
    context = ContextBuilder()
    tools = ToolRegistry(workspace_root=".", tool_configs=cfg.tools)
    
    # 3. Setup provider
    api_key = os.environ.get("OPENROUTER_API_KEY")
    provider = OpenRouterAdapter(api_key=api_key, model=cfg.model)
    
    # 4. Compose Agent Service
    return AgentService(
        provider=provider,
        session_manager=sessions,
        context_builder=context,
        tools=tools
    )
