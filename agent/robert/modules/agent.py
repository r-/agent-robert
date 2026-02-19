"""Agent module — handles prompt construction and the LLM interaction loop."""

__all__ = ["AgentPort", "AgentResponse", "ContextBuilder", "AgentService"]

# ─── API (public contract) ───────────────────────────

from dataclasses import dataclass
from typing import Protocol

@dataclass
class AgentResponse:
    content: str
    iterations: int

class AgentPort(Protocol):
    async def process(self, message: str, session_key: str) -> AgentResponse: ...


import json
from robert.modules.tools import ToolRegistry

class AgentService:
    """The core agent logic.
    
    Wires together context building, provider calling, and tool execution.
    """
    def __init__(self, provider, session_manager, context_builder, tools: ToolRegistry):
        self._provider = provider
        self._sessions = session_manager
        self._context = context_builder
        self._tools = tools
        self._max_iterations = 20

    async def process(self, message: str, session_key: str) -> AgentResponse:
        # 1. Load session
        session = self._sessions.get_session(session_key)
        
        if message.startswith("data:audio"):
            # It's an audio payload
            session.add_user_audio_message(message)
        else:
            session.add_user_message(message)
        
        # 2. Build system prompt
        tool_schemas = self._tools.get_all_schemas()
        system_prompt = self._context.build_system_prompt(tools=tool_schemas)
        
        iterations = 0
        while iterations < self._max_iterations:
            iterations += 1
            
            # 3. Call LLM
            messages = session.get_messages_for_llm(system_prompt)
            response = await self._provider.chat(messages, tools=tool_schemas)
            
            # 4. Handle tool calls
            if response.tool_calls:
                # Add the 'assistant' message with tool_calls to history
                session.add_tool_call_message(response.content, response.tool_calls)
                
                for tc in response.tool_calls:
                    f = tc.get("function", {})
                    name = f.get("name")
                    args = json.loads(f.get("arguments", "{}"))
                    call_id = tc.get("id")
                    
                    # Execute tool
                    result = await self._tools.call(name, **args)
                    
                    # Add 'tool' result message to history
                    session.add_tool_result_message(call_id, result.content)
                
                # Continue loop to let LLM see the tool outputs
                continue
            
            # 5. Final response (no tool calls)
            session.add_assistant_message(response.content)
            return AgentResponse(content=response.content, iterations=iterations)

        return AgentResponse(content="Error: Max iterations reached", iterations=iterations)


class ContextBuilder:
    """Assembles the system prompt from static identity and bundled skills."""
    def __init__(self, identity: str = "You are Agent R.O.B.E.R.T."):
        self._identity = identity

    def build_system_prompt(self, tools: list[dict] = None) -> str:
        prompt = [
            self._identity,
            "You follow the 'Pragmatic Modular Monolith' architecture principles.",
            "You have access to local tools. If a tool can help, use it immediately.",
            "You are multimodal: you can hear audio inputs sent by the user. If you receive audio, answer it naturally."
        ]
        
        if tools:
            prompt.append("\nAvailable tools:")
            for t in tools:
                f = t.get("function", {})
                prompt.append(f"- {f.get('name')}: {f.get('description')}")
                
        return "\n".join(prompt)


# ─── INTERNAL (private — do not import from outside) ──
