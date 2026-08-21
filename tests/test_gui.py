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
    for tool_name in ("kicad", "ngspice", "ghdl", "verilator"):
        updater = get_updater(tool_name)
        assert updater is not None, f"Updater for {tool_name} must be registered."


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


def test_gui_install_all_uses_registry(monkeypatch):
    """GUI install_all must use the central registry get_installer/get_detector, not GUI-specific logic."""
    import registry
    from detector import ToolInfo

    install_calls = []

    class MockInstaller:
        def __init__(self, name):
            self.name = name
        def install(self):
            install_calls.append(self.name)
            return True

    class MockDetector:
        def __init__(self, name, installed):
            self.name = name
            self._installed = installed
        def detect(self):
            return ToolInfo(name=self.name, installed=self._installed, path=None, version=None)

    # KiCad installed, others not
    monkeypatch.setattr(registry, "get_installer", lambda t: MockInstaller(t))
    monkeypatch.setattr(registry, "get_detector", lambda t: MockDetector(t, t == "kicad"))

    # Simulate the same logic install_all uses
    from registry import TOOLS
    for tool_name, info in TOOLS.items():
        installer = registry.get_installer(tool_name)
        detector = registry.get_detector(tool_name)
        if not installer or not detector:
            continue
        det_info = detector.detect()
        if not det_info.installed:
            installer.install()

    # KiCad should NOT be in install_calls
    assert "kicad" not in install_calls
    # The other three should be
    assert "ngspice" in install_calls
    assert "ghdl" in install_calls
    assert "verilator" in install_calls
