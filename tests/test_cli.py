import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from manager import main


def test_cli_list(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["esim-manager", "list"])
    main()
    captured = capsys.readouterr()
    assert "KiCad" in captured.out
    assert "Ngspice" in captured.out


def test_cli_check(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["esim-manager", "check"])
    main()
    captured = capsys.readouterr()
    assert "eSim Tool Manager Status Check" in captured.out


def test_cli_doctor(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["esim-manager", "doctor"])
    main()
    captured = capsys.readouterr()
    assert "eSim Environment Doctor" in captured.out


def test_cli_config(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["esim-manager", "config"])
    main()
    captured = capsys.readouterr()
    assert "eSim Tool Manager Configuration" in captured.out


def test_cli_install_all_skips_installed(monkeypatch, capsys):
    """'install all' should skip tools that are already installed."""
    from detector import ToolInfo
    monkeypatch.setattr("sys.argv", ["esim-manager", "install", "all"])

    # Mock all detectors to report installed via manager module binding
    class MockDetector:
        def detect(self):
            return ToolInfo(name="Tool", installed=True, path="tool.exe", version="1.0")

    import manager
    monkeypatch.setattr(manager, "get_detector", lambda t: MockDetector())

    main()
    captured = capsys.readouterr()
    assert "already installed, skipping" in captured.out
    assert "All installation tasks completed" in captured.out


def test_cli_install_all_installs_missing(monkeypatch, capsys):
    """'install all' should install tools whose detectors report not-installed."""
    from detector import ToolInfo

    monkeypatch.setattr("sys.argv", ["esim-manager", "install", "all"])

    # KiCad installed, others not — mock via manager module binding
    class MockDetector:
        def __init__(self, installed):
            self._installed = installed
        def detect(self):
            return ToolInfo(name="Tool", installed=self._installed, path="path" if self._installed else None, version="1.0" if self._installed else None)

    import manager
    monkeypatch.setattr(manager, "get_detector", lambda t: MockDetector(installed=(t == "kicad")))

    # Mock all installers to succeed
    class MockInstaller:
        def install(self):
            return True
    monkeypatch.setattr(manager, "get_installer", lambda t: MockInstaller())

    main()
    captured = capsys.readouterr()
    assert "KiCad: already installed, skipping" in captured.out


def test_cli_install_all_continues_on_failure(monkeypatch, capsys):
    """'install all' should continue when one tool fails and report the failure."""
    from detector import ToolInfo

    monkeypatch.setattr("sys.argv", ["esim-manager", "install", "all"])

    # Mock all detectors to report not-installed via the manager module's binding
    class MockDetector:
        def detect(self):
            return ToolInfo(name="Tool", installed=False, path=None, version=None)

    import manager
    monkeypatch.setattr(manager, "get_detector", lambda t: MockDetector())

    # KiCad fails, others succeed
    call_log = []
    class FailInstaller:
        def install(self):
            call_log.append("fail")
            return False
    class SuccessInstaller:
        def install(self):
            call_log.append("success")
            return True

    def mock_installer(t):
        if t == "kicad":
            return FailInstaller()
        return SuccessInstaller()
    monkeypatch.setattr(manager, "get_installer", mock_installer)

    main()
    captured = capsys.readouterr()
    # Should report failure but continue
    assert "failure" in captured.out.lower()
    # All 4 tools should have been attempted
    assert len(call_log) == 4
