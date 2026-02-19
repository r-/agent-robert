import pytest
import os
from robert.modules.tools import _is_safe_path

def test_safe_path_checks():
    base = os.path.abspath("workspace")
    
    # Valid paths
    assert _is_safe_path(base, "file.txt") is True
    assert _is_safe_path(base, "sub/dir/file.py") is True
    assert _is_safe_path(base, "./file.txt") is True
    
    # Escape attempts
    assert _is_safe_path(base, "../outside.txt") is False
    assert _is_safe_path(base, "/etc/passwd") is False
    assert _is_safe_path(base, "sub/../../outside.txt") is False

@pytest.mark.asyncio
async def test_read_file_tool(tmp_path):
    from robert.modules.tools import _ReadFileTool
    
    workspace = tmp_path / "work"
    workspace.mkdir()
    secret_file = tmp_path / "secret.txt"
    secret_file.write_text("shhh")
    
    allowed_file = workspace / "hello.txt"
    allowed_file.write_text("world")
    
    tool = _ReadFileTool(str(workspace))
    
    # Test valid read
    result = await tool.execute("hello.txt")
    assert result.content == "world"
    assert result.is_error is False
    
    # Test invalid read (outside workspace)
    result = await tool.execute("../secret.txt")
    assert "Access denied" in result.content
    assert result.is_error is True
