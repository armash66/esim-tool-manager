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
