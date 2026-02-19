"""Tools module - local tool implementations with security sandboxing."""

__all__ = ["ToolRegistry", "ToolPort", "ToolResult"]

# ─── API (public contract) ───────────────────────────

from dataclasses import dataclass
from typing import Any, Protocol
import os
import subprocess

@dataclass
class ToolResult:
    content: str
    is_error: bool = False

class ToolPort(Protocol):
    def get_schema(self) -> dict: ...
    async def execute(self, **kwargs) -> ToolResult: ...

class ToolRegistry:
    """Manages available tools and their security policies."""
    def __init__(self, workspace_root: str, tool_configs: dict):
        self._workspace = os.path.abspath(workspace_root)
        self._configs = tool_configs
        self._tools: dict[str, ToolPort] = {}
        self._register_defaults()

    def _register_defaults(self):
        # Read-only file (Always enabled, but restricted)
        self.register("read_file", _ReadFileTool(self._workspace))
        
        # Write file (Disabled by default)
        if self._configs.get("fileWrite", {}).enabled:
            self.register("write_file", _WriteFileTool(self._workspace))
            
        # Shell exec (Disabled by default + Allowlist)
        shell_cfg = self._configs.get("shell", {})
        if shell_cfg.enabled:
            self.register("exec_shell", _ShellTool(self._workspace, shell_cfg.allowlist))

        # Home Assistant (Disabled by default)
        ha_cfg = self._configs.get("homeassistant", {})
        if ha_cfg.enabled:
            # We need to get secrets from env, not config for security
            ha_url = os.environ.get("HOMEASSISTANT_URL", "")
            ha_token = os.environ.get("HOMEASSISTANT_TOKEN", "")
            
            if ha_url and ha_token:
                from robert.modules.tools_ha import HAGetStateTool, HACallServiceTool, HAListEntitiesTool
                self.register("ha_get_state", HAGetStateTool(ha_url, ha_token))
                self.register("ha_call_service", HACallServiceTool(ha_url, ha_token))
                self.register("ha_list_entities", HAListEntitiesTool(ha_url, ha_token))

    def register(self, name: str, tool: ToolPort):
        self._tools[name] = tool

    def get_all_schemas(self) -> list[dict]:
        return [t.get_schema() for t in self._tools.values()]

    async def call(self, name: str, **kwargs) -> ToolResult:
        if name not in self._tools:
            return ToolResult(content=f"Error: Tool '{name}' not found or disabled.", is_error=True)
        return await self._tools[name].execute(**kwargs)

# ─── INTERNAL (private implementations) ──────────────

def _is_safe_path(base: str, path: str) -> bool:
    """Check if the resolved path is inside the base directory."""
    try:
        abs_path = os.path.abspath(os.path.join(base, path))
        return abs_path.startswith(base)
    except (ValueError, TypeError):
        return False

class _ReadFileTool:
    def __init__(self, workspace: str):
        self._workspace = workspace

    def get_schema(self):
        return {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read the content of a file within the allowed workspace.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Relative path to file."}
                    },
                    "required": ["path"]
                }
            }
        }

    async def execute(self, path: str):
        if not _is_safe_path(self._workspace, path):
            return ToolResult("Error: Access denied. Path is outside workspace.", is_error=True)
        try:
            with open(os.path.join(self._workspace, path), "r", encoding="utf-8") as f:
                return ToolResult(f.read())
        except Exception as e:
            return ToolResult(f"Error reading file: {str(e)}", is_error=True)

class _WriteFileTool:
    def __init__(self, workspace: str):
        self._workspace = workspace

    def get_schema(self):
        return {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Create or overwrite a file with specific content.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Relative path to destination."},
                        "content": {"type": "string", "description": "File content."}
                    },
                    "required": ["path", "content"]
                }
            }
        }

    async def execute(self, path: str, content: str):
        if not _is_safe_path(self._workspace, path):
            return ToolResult("Error: Access denied. Path is outside workspace.", is_error=True)
        try:
            with open(os.path.join(self._workspace, path), "w", encoding="utf-8") as f:
                f.write(content)
                return ToolResult(f"File '{path}' written successfully.")
        except Exception as e:
            return ToolResult(f"Error writing file: {str(e)}", is_error=True)

class _ShellTool:
    def __init__(self, workspace: str, allowlist: list[str]):
        self._workspace = workspace
        self._allowlist = allowlist

    def get_schema(self):
        return {
            "type": "function",
            "function": {
                "name": "exec_shell",
                "description": "Execute a shell command from the allowlist.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Command to run."}
                    },
                    "required": ["command"]
                }
            }
        }

    async def execute(self, command: str):
        # 1. Check Allowlist
        cmd_base = command.split()[0].lower() if command else ""
        if cmd_base not in [a.lower() for a in self._allowlist]:
            return ToolResult(f"Error: Command '{cmd_base}' is not in the allowlist ({self._allowlist}).", is_error=True)

        # 2. Execute
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                cwd=self._workspace, 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            out = result.stdout + result.stderr
            return ToolResult(out if out else f"(Exit Code {result.returncode})")
        except Exception as e:
            return ToolResult(f"Error executing command: {str(e)}", is_error=True)
