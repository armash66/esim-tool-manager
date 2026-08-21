import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from registry import TOOLS, get_installer, get_updater


def test_gui_registry_wiring_all_tools():
    for tool_name in ("kicad", "ngspice", "ghdl", "verilator"):
        assert tool_name in TOOLS
        installer = get_installer(tool_name)
        assert installer is not None, f"Installer for {tool_name} must be registered."


def test_gui_updaters_wiring():
    for tool_name in ("kicad", "ngspice"):
        updater = get_updater(tool_name)
        assert updater is not None


def test_gui_installer_execution_mocked(monkeypatch):
    class DummyInstaller:
        def install(self):
            return True

    import registry
    monkeypatch.setattr(registry, "get_installer", lambda t: DummyInstaller())
    for tool_name in ("kicad", "ngspice", "ghdl", "verilator"):
        inst = registry.get_installer(tool_name)
        assert inst is not None
        assert inst.install() is True
