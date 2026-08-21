import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from registry import get_detector, get_installer, list_tools, TOOLS


def test_list_tools():
    tools = list_tools()
    assert "kicad" in tools
    assert "ngspice" in tools
    assert "ghdl" in tools
    assert "verilator" in tools


def test_get_detector_and_installer_valid():
    assert get_detector("kicad") is not None
    assert get_installer("kicad") is not None
    assert get_detector("ngspice") is not None
    assert get_installer("ngspice") is not None


def test_unknown_tool_rejection():
    assert get_detector("unknown_tool") is None
    assert get_installer("unknown_tool") is None
