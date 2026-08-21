import json
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from installer import KiCadInstaller, NgspiceInstaller, GhdlInstaller, VerilatorInstaller


def test_ngspice_installer_missing_archive(tmp_path):
    missing_archive = tmp_path / "nonexistent.7z"
    installer = NgspiceInstaller(missing_archive)
    assert installer.install() is False


def test_kicad_installer_winget_missing(monkeypatch):
    from detector import ToolInfo
    monkeypatch.setattr(
        "detector.KiCadDetector.detect",
        lambda self: ToolInfo(name="KiCad", installed=False, path=None, version=None),
    )
    monkeypatch.setattr("installer.find_winget", lambda: None)
    installer = KiCadInstaller()
    assert installer.install() is False


def test_ghdl_installer_winget_missing(monkeypatch):
    monkeypatch.setattr("installer.find_winget", lambda: None)
    installer = GhdlInstaller()
    assert installer.install() is False


def test_verilator_installer_missing(monkeypatch):
    monkeypatch.setattr("pathlib.Path.is_file", lambda self: False)
    installer = VerilatorInstaller()
    assert installer.install() is False


def test_kicad_uninstall_winget_missing(monkeypatch):
    monkeypatch.setattr("installer.find_winget", lambda: None)
    installer = KiCadInstaller()
    assert installer.uninstall() is False


def test_ngspice_uninstall(tmp_path, monkeypatch):
    install_dir = tmp_path / "ngspice"
    install_dir.mkdir(parents=True, exist_ok=True)
    installer = NgspiceInstaller(tmp_path / "fake.7z")
    installer.install_dir = install_dir
    assert installer.uninstall() is True
    assert not install_dir.exists()


def test_kicad_install_reports_failure_when_detector_finds_nothing(monkeypatch):
    """Regression: installer must not report success if KiCadDetector cannot find the executable."""
    from detector import ToolInfo

    # Pre-check returns not installed, post-install also returns not installed
    monkeypatch.setattr("installer.find_winget", lambda: "winget.exe")
    monkeypatch.setattr("subprocess.run", lambda *a, **kw: type("R", (), {"returncode": 0, "stdout": "", "stderr": ""})())
    monkeypatch.setattr(
        "detector.KiCadDetector.detect",
        lambda self: ToolInfo(name="KiCad", installed=False, path=None, version=None),
    )

    installer = KiCadInstaller()
    result = installer.install()
    assert result is False, "install() must return False when detector cannot find the executable"


def test_kicad_install_reports_success_when_detector_confirms(monkeypatch):
    """Installer should return True only when the detector verifies the executable exists."""
    from detector import ToolInfo

    # Pre-check returns installed → should short-circuit and return True immediately
    monkeypatch.setattr(
        "detector.KiCadDetector.detect",
        lambda self: ToolInfo(name="KiCad", installed=True, path="C:\\kicad\\bin\\kicad-cli.exe", version="10.0.5"),
    )

    installer = KiCadInstaller()
    result = installer.install()
    assert result is True


def test_kicad_install_scope_user_force_recovery(monkeypatch):
    """Regression: WinGet has stale registration but executable is missing.
    install() should use --scope user --force, then detect the newly installed executable."""
    from detector import ToolInfo

    call_count = {"n": 0}

    def detect_side_effect(self):
        call_count["n"] += 1
        if call_count["n"] == 1:
            # Pre-check: not installed (stale WinGet state, executable missing)
            return ToolInfo(name="KiCad", installed=False, path=None, version=None)
        else:
            # Post-install: WinGet --force recovered the installation
            return ToolInfo(
                name="KiCad", installed=True,
                path="C:\\Users\\test\\AppData\\Local\\Programs\\KiCad\\10.0\\bin\\kicad-cli.exe",
                version="10.0.5"
            )

    monkeypatch.setattr("installer.find_winget", lambda: "winget.exe")
    monkeypatch.setattr("subprocess.run", lambda *a, **kw: type("R", (), {"returncode": 0, "stdout": "OK", "stderr": ""})())
    monkeypatch.setattr("detector.KiCadDetector.detect", detect_side_effect)

    installer = KiCadInstaller()
    result = installer.install()
    assert result is True
    assert call_count["n"] == 2, "Detector must be called twice: pre-check + post-install verification"
