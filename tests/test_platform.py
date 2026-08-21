import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from platform_adapter import get_platform_adapter, WindowsAdapter, LinuxAdapter


def test_platform_adapter_selection():
    adapter = get_platform_adapter()
    assert adapter is not None
    assert adapter.get_name() in ("Windows", "Linux")


def test_windows_adapter_path_formatting():
    adapter = WindowsAdapter()
    instructions = adapter.format_path_instructions(["C:\\Tools\\bin"])
    assert "$env:Path" in instructions
    assert "C:\\Tools\\bin" in instructions


def test_linux_adapter_path_formatting():
    adapter = LinuxAdapter()
    instructions = adapter.format_path_instructions(["/usr/local/bin"])
    assert "export PATH" in instructions
    assert "/usr/local/bin" in instructions
