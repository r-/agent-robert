"""Home Assistant Tools — Enables control of HA entities via REST API."""

from dataclasses import dataclass
import os
import json
import httpx
from typing import Any, Protocol

# ─── API (public contract) ───────────────────────────

@dataclass
class HAServiceCall:
    domain: str
    service: str
    entity_id: str

class HomeAssistantTool:
    """Base class for HA tools."""
    def __init__(self, ha_url: str, ha_token: str):
        self._url = ha_url.rstrip("/")
        self._token = ha_token
        self._headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

    async def _get(self, endpoint: str) -> dict | list:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self._url}/api/{endpoint}", headers=self._headers)
            resp.raise_for_status()
            return resp.json()

    async def _post(self, endpoint: str, data: dict) -> list:
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self._url}/api/{endpoint}", headers=self._headers, json=data)
            resp.raise_for_status()
            return resp.json()


class HAGetStateTool(HomeAssistantTool):
    """Tool to get the state of a specific entity."""
    def get_schema(self):
        return {
            "type": "function",
            "function": {
                "name": "ha_get_state",
                "description": "Get the current state and attributes of a Home Assistant entity.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "entity_id": {"type": "string", "description": "The entity ID (e.g. light.living_room)."}
                    },
                    "required": ["entity_id"]
                }
            }
        }

    async def execute(self, entity_id: str) -> str:
        # Check if executed as a tool call which wraps args in another dict? No, simple kwargs.
        try:
            state = await self._get(f"states/{entity_id}")
            # Format nicely for LLM
            s = state.get("state", "unknown")
            attrs = state.get("attributes", {})
            friendly_name = attrs.get("friendly_name", entity_id)
            return f"Entity '{friendly_name}' ({entity_id}) is {s}. Attributes: {json.dumps(attrs)}"
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return f"Entity '{entity_id}' not found."
            return f"Error getting state: {e}"
        except Exception as e:
            return f"Connection error: {e}"

class HACallServiceTool(HomeAssistantTool):
    """Tool to call a service (turn_on, turn_off, etc)."""
    def get_schema(self):
        return {
            "type": "function",
            "function": {
                "name": "ha_call_service",
                "description": "Call a service on a Home Assistant entity (e.g. turn_on, turn_off).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "domain": {"type": "string", "description": "Service domain (e.g. light, switch)."},
                        "service": {"type": "string", "description": "Service name (e.g. turn_on)."},
                        "entity_id": {"type": "string", "description": "Target entity ID."}
                    },
                    "required": ["domain", "service", "entity_id"]
                }
            }
        }

    async def execute(self, domain: str, service: str, entity_id: str) -> str:
        try:
            # e.g. POST /api/services/light/turn_on
            data = {"entity_id": entity_id}
            await self._post(f"services/{domain}/{service}", data)
            return f"Service {domain}.{service} called for {entity_id}."
        except Exception as e:
            return f"Error calling service: {e}"

class HAListEntitiesTool(HomeAssistantTool):
    """Tool to list all available entities (for discovery)."""
    def get_schema(self):
        return {
            "type": "function",
            "function": {
                "name": "ha_list_entities",
                "description": "List available Home Assistant entities to discover device names.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "domain": {"type": "string", "description": "Optional domain filter (e.g. light)."}
                    },
                }
            }
        }

    async def execute(self, domain: str = None) -> str:
        try:
            states = await self._get("states")
            # Filter and summarize
            results = []
            for s in states:
                eid = s["entity_id"]
                if domain and not eid.startswith(domain + "."):
                    continue
                
                friendly = s.get("attributes", {}).get("friendly_name", eid)
                state = s["state"]
                results.append(f"- {eid} ({friendly}): {state}")
            
            # Limit output to avoid context overflow
            return "\n".join(results[:50]) or "No entities found."
        except Exception as e:
            return f"Error listing entities: {e}"
