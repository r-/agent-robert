"""Agent-Robert: Public Python API

This file exposes the clean API for external consumers (like api-router).
No web dependencies, pure Python.
"""

from robert.modules.agent import AgentResponse

__all__ = ["process"]

# Lazy-initialized singleton (avoids import-time side effects)
_agent = None

def _get_agent():
    global _agent
    if _agent is None:
        from robert.composition.startup import create_agent_service
        _agent = create_agent_service()
    return _agent

async def process(message: str, session_key: str = "default") -> AgentResponse:
    """The primary integration point for R.O.B.E.R.T.
    
    Usage:
        import robert
        resp = await robert.process("hello", "user1")
        print(resp.content)
    """
    return await _get_agent().process(message, session_key)
