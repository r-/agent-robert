import os
import json
from robert.modules.config import load_config, AgentConfig

def test_load_config_defaults(tmp_path):
    # Test loading when file doesn't exist
    config = load_config("non_existent_file.json")
    assert isinstance(config, AgentConfig)
    assert config.provider == "openrouter"
    assert config.model == "google/gemini-2.0-flash-001"

def test_load_config_from_json(tmp_path):
    config_file = tmp_path / "config.json"
    data = {
        "provider": "custom-provider",
        "model": "custom-model",
        "tools": {
            "shell": {"enabled": True, "allowlist": ["ls"]}
        }
    }
    config_file.write_text(json.dumps(data))
    
    config = load_config(str(config_file))
    assert config.provider == "custom-provider"
    assert config.model == "custom-model"
    assert config.tools["shell"].enabled is True
    assert config.tools["shell"].allowlist == ["ls"]
    assert config.tools["fileWrite"].enabled is False # Default remains
