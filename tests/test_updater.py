import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from updater import GhdlUpdater, VerilatorUpdater, KiCadUpdater, NgspiceUpdater
from detector import ToolInfo


def test_ghdl_updater_up_to_date(monkeypatch):
    """Test GHDL check_update when installed version equals available version."""
    monkeypatch.setattr(
        "detector.GhdlDetector.detect",
        lambda self: ToolInfo(name="GHDL", installed=True, path="ghdl.exe", version="6.0.0"),
    )
    monkeypatch.setattr("updater.get_winget_latest_version", lambda pkg_id: "6.0.0")

    updater = GhdlUpdater()
    st = updater.check_update()
    assert st["installed"] is True
    assert st["installed_version"] == "6.0.0"
    assert st["latest_version"] == "6.0.0"
    assert st["needs_update"] is False
    assert st["error"] is None


def test_ghdl_updater_older_version(monkeypatch):
    """Test GHDL check_update when installed version is older."""
    monkeypatch.setattr(
        "detector.GhdlDetector.detect",
        lambda self: ToolInfo(name="GHDL", installed=True, path="ghdl.exe", version="5.0.0"),
    )
    monkeypatch.setattr("updater.get_winget_latest_version", lambda pkg_id: "6.0.0")

    updater = GhdlUpdater()
    st = updater.check_update()
    assert st["installed"] is True
    assert st["installed_version"] == "5.0.0"
    assert st["latest_version"] == "6.0.0"
    assert st["needs_update"] is True
    assert st["error"] is None


def test_verilator_updater_up_to_date(monkeypatch):
    """Test Verilator check_update when installed version equals available version."""
    monkeypatch.setattr(
        "detector.VerilatorDetector.detect",
        lambda self: ToolInfo(name="Verilator", installed=True, path="verilator.exe", version="5.040"),
    )
    monkeypatch.setattr("updater.get_winget_latest_version", lambda pkg_id: "5.040")

    updater = VerilatorUpdater()
    st = updater.check_update()
    assert st["installed"] is True
    assert st["installed_version"] == "5.040"
    assert st["latest_version"] == "5.040"
    assert st["needs_update"] is False
    assert st["error"] is None


def test_verilator_updater_older_version(monkeypatch):
    """Test Verilator check_update when installed version is older."""
    monkeypatch.setattr(
        "detector.VerilatorDetector.detect",
        lambda self: ToolInfo(name="Verilator", installed=True, path="verilator.exe", version="5.030"),
    )
    monkeypatch.setattr("updater.get_winget_latest_version", lambda pkg_id: "5.040")

    updater = VerilatorUpdater()
    st = updater.check_update()
    assert st["installed"] is True
    assert st["installed_version"] == "5.030"
    assert st["latest_version"] == "5.040"
    assert st["needs_update"] is True
    assert st["error"] is None


def test_updater_unavailable_version_source(monkeypatch):
    """Test updater handling network/version source failure gracefully."""
    monkeypatch.setattr(
        "detector.GhdlDetector.detect",
        lambda self: ToolInfo(name="GHDL", installed=True, path="ghdl.exe", version="6.0.0"),
    )
    monkeypatch.setattr("updater.get_winget_latest_version", lambda pkg_id: None)

    updater = GhdlUpdater()
    st = updater.check_update()
    assert st["installed"] is True
    assert st["installed_version"] == "6.0.0"
    assert st["latest_version"] is None
    assert st["needs_update"] is False
    assert st["error"] == "Unable to determine latest version"


def test_updater_malformed_version_handling(monkeypatch):
    """Test comparison fallback when version strings are non-standard semver."""
    monkeypatch.setattr(
        "detector.GhdlDetector.detect",
        lambda self: ToolInfo(name="GHDL", installed=True, path="ghdl.exe", version="custom-v1"),
    )
    monkeypatch.setattr("updater.get_winget_latest_version", lambda pkg_id: "custom-v2")

    updater = GhdlUpdater()
    st = updater.check_update()
    assert st["installed"] is True
    assert st["needs_update"] is True


def test_verilator_updater_pacman_missing(monkeypatch):
    """Regression: test VerilatorUpdater when winget fails and pacman is completely unavailable."""
    monkeypatch.setattr(
        "detector.VerilatorDetector.detect",
        lambda self: ToolInfo(name="Verilator", installed=True, path="verilator.exe", version="5.040"),
    )
    monkeypatch.setattr("updater.get_winget_latest_version", lambda pkg_id: None)
    monkeypatch.setattr("shutil.which", lambda cmd: None)
    monkeypatch.setattr("pathlib.Path.is_file", lambda self: False)

    updater = VerilatorUpdater()
    st = updater.check_update()
    assert st["installed"] is True
    assert st["installed_version"] == "5.040"
    assert st["latest_version"] is None
    assert st["error"] == "Unable to determine latest version"


def test_verilator_updater_pacman_via_shutil_which(monkeypatch):
    """Test VerilatorUpdater when pacman is available directly via shutil.which."""
    monkeypatch.setattr(
        "detector.VerilatorDetector.detect",
        lambda self: ToolInfo(name="Verilator", installed=True, path="verilator.exe", version="5.030"),
    )
    monkeypatch.setattr("updater.get_winget_latest_version", lambda pkg_id: None)
    monkeypatch.setattr("shutil.which", lambda cmd: "/usr/bin/pacman" if cmd == "pacman" else None)

    class MockRun:
        returncode = 0
        stdout = "Repository : mingw64\nName : mingw-w64-x86_64-verilator\nVersion : 5.040-1\n"

    monkeypatch.setattr("subprocess.run", lambda *a, **kw: MockRun())

    updater = VerilatorUpdater()
    st = updater.check_update()
    assert st["installed"] is True
    assert st["installed_version"] == "5.030"
    assert st["latest_version"] == "5.040"
    assert st["needs_update"] is True


def test_verilator_updater_pacman_off_path_standard_location(monkeypatch, tmp_path):
    """Test VerilatorUpdater when pacman is NOT on PATH, but present at standard C:/msys64 location."""
    monkeypatch.setattr(
        "detector.VerilatorDetector.detect",
        lambda self: ToolInfo(name="Verilator", installed=True, path="verilator.exe", version="5.040"),
    )
    monkeypatch.setattr("updater.get_winget_latest_version", lambda pkg_id: None)
    monkeypatch.setattr("shutil.which", lambda cmd: None)
    monkeypatch.setattr("sys.platform", "win32")

    fake_pacman = tmp_path / "pacman.exe"
    fake_pacman.write_text("fake binary")

    original_is_file = Path.is_file
    def mock_is_file(self):
        if "msys64" in str(self):
            return True
        return original_is_file(self)

    monkeypatch.setattr("pathlib.Path.is_file", mock_is_file)

    class MockRun:
        returncode = 0
        stdout = "Version : 5.040-1\n"

    monkeypatch.setattr("subprocess.run", lambda *a, **kw: MockRun())

    updater = VerilatorUpdater()
    st = updater.check_update()
    assert st["installed"] is True
    assert st["installed_version"] == "5.040"
    assert st["latest_version"] == "5.040"
    assert st["needs_update"] is False


def test_verilator_updater_pacman_execution_failure(monkeypatch):
    """Test VerilatorUpdater when pacman exists but subprocess fails."""
    monkeypatch.setattr(
        "detector.VerilatorDetector.detect",
        lambda self: ToolInfo(name="Verilator", installed=True, path="verilator.exe", version="5.040"),
    )
    monkeypatch.setattr("updater.get_winget_latest_version", lambda pkg_id: None)
    monkeypatch.setattr("shutil.which", lambda cmd: "pacman")

    class MockRunFail:
        returncode = 1
        stdout = ""

    monkeypatch.setattr("subprocess.run", lambda *a, **kw: MockRunFail())

    updater = VerilatorUpdater()
    st = updater.check_update()
    assert st["installed"] is True
    assert st["latest_version"] is None
    assert st["error"] == "Unable to determine latest version"
