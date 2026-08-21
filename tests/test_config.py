import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import load_config, save_config, DEFAULT_CONFIG


def test_default_config_creation(monkeypatch, tmp_path):
    test_cfg_path = tmp_path / ".esim-tools" / "config.json"
    monkeypatch.setattr("config.CONFIG_PATH", test_cfg_path)

    cfg = load_config()
    assert test_cfg_path.is_file()
    assert cfg["auto_update"] == False
    assert "install_directory" in cfg


def test_missing_key_fallback(monkeypatch, tmp_path):
    test_cfg_path = tmp_path / ".esim-tools" / "config.json"
    monkeypatch.setattr("config.CONFIG_PATH", test_cfg_path)

    # Save custom config missing auto_update key
    test_cfg_path.parent.mkdir(parents=True, exist_ok=True)
    test_cfg_path.write_text('{"install_directory": "/custom/path"}')

    cfg = load_config()
    assert cfg["install_directory"] == "/custom/path"
    assert cfg["auto_update"] == False
