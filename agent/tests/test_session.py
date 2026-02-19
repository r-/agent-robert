import json
import os
from robert.modules.session import Session, Message

def test_session_message_flow(tmp_path):
    session_file = tmp_path / "test.jsonl"
    session = Session("test-key", str(session_file))
    
    # Add messages
    session.add_user_message("hello")
    session.add_assistant_message("hi")
    
    # Verify file content
    lines = session_file.read_text().splitlines()
    assert len(lines) == 2
    
    data0 = json.loads(lines[0])
    assert data0["role"] == "user"
    assert data0["content"] == "hello"
    
    data1 = json.loads(lines[1])
    assert data1["role"] == "assistant"
    assert data1["content"] == "hi"

def test_session_loading(tmp_path):
    session_file = tmp_path / "load.jsonl"
    session_file.write_text(json.dumps({"role": "user", "content": "saved", "timestamp": "2024-01-01"}) + "\n")
    
    session = Session("load-key", str(session_file))
    msgs = session.get_messages_for_llm("sys")
    
    assert len(msgs) == 2 # system + user
    assert msgs[0]["role"] == "system"
    assert msgs[1]["content"] == "saved"
