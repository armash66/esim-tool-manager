import json
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from detector import KiCadDetector, NgspiceDetector, GhdlDetector, VerilatorDetector


def test_ngspice_detector_with_metadata(monkeypatch, tmp_path):
    install_dir = tmp_path / ".esim-tools"
    monkeypatch.setattr("detector.get_install_dir", lambda: install_dir)

    # Create fake executable and metadata
    exe = install_dir / "ngspice" / "Spice64" / "bin" / "ngspice.exe"
    exe.parent.mkdir(parents=True, exist_ok=True)
    exe.write_text("fake binary")

    metadata_file = install_dir / "ngspice" / "metadata.json"
    metadata_file.write_text(json.dumps({"name": "ngspice", "version": "47", "path": str(exe)}))

    info = NgspiceDetector().detect()
    assert info.installed is True
    assert info.version == "47"
    assert info.path == str(exe)


def test_ngspice_detector_missing(monkeypatch, tmp_path):
    install_dir = tmp_path / ".esim-tools"
    monkeypatch.setattr("detector.get_install_dir", lambda: install_dir)
    monkeypatch.setattr("shutil.which", lambda name: None)

    info = NgspiceDetector().detect()
    assert info.installed is False
    assert info.path is None
    assert info.version is None


def test_ghdl_detector_missing(monkeypatch, tmp_path):
    monkeypatch.setattr("shutil.which", lambda name: None)
    fake_home = tmp_path / "user"
    monkeypatch.setattr("pathlib.Path.home", lambda: fake_home)

    info = GhdlDetector().detect()
    assert info.installed is False
    assert info.path is None


def test_verilator_detector_missing(monkeypatch, tmp_path):
    monkeypatch.setattr("shutil.which", lambda name: None)
    monkeypatch.setattr("pathlib.Path.is_file", lambda self: False)
    fake_home = tmp_path / "user"
    monkeypatch.setattr("pathlib.Path.home", lambda: fake_home)

    info = VerilatorDetector().detect()
    assert info.installed is False
    assert info.path is None


def test_kicad_detector_finds_per_user_install(monkeypatch, tmp_path):
    """Regression: KiCad 10.x installs per-user via WinGet to %LOCALAPPDATA%/Programs/KiCad."""
    monkeypatch.setattr("shutil.which", lambda name: None)
    monkeypatch.setattr("sys.platform", "win32")

    local_app = tmp_path / "AppData" / "Local"
    kicad_dir = local_app / "Programs" / "KiCad" / "10.0" / "bin"
    kicad_dir.mkdir(parents=True)
    kicad_exe = kicad_dir / "kicad-cli.exe"
    kicad_exe.write_text("fake")

    monkeypatch.setenv("LOCALAPPDATA", str(local_app))
    monkeypatch.setenv("ProgramFiles", str(tmp_path / "nonexistent"))

    monkeypatch.setattr(
        "subprocess.run",
        lambda cmd, **kw: type("R", (), {"returncode": 0, "stdout": "10.0.5"})(),
    )

    info = KiCadDetector().detect()
    assert info.installed is True
    assert info.path == str(kicad_exe)
    assert info.version == "10.0.5"


def test_kicad_detector_finds_program_files_install(monkeypatch, tmp_path):
    """KiCad may also be installed system-wide to %ProgramFiles%/KiCad."""
    monkeypatch.setattr("shutil.which", lambda name: None)
    monkeypatch.setattr("sys.platform", "win32")

    prog_files = tmp_path / "ProgramFiles"
    kicad_dir = prog_files / "KiCad" / "10.0" / "bin"
    kicad_dir.mkdir(parents=True)
    kicad_exe = kicad_dir / "kicad-cli.exe"
    kicad_exe.write_text("fake")

    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "nonexistent"))
    monkeypatch.setenv("ProgramFiles", str(prog_files))

    monkeypatch.setattr(
        "subprocess.run",
        lambda cmd, **kw: type("R", (), {"returncode": 0, "stdout": "10.0.5"})(),
    )

    info = KiCadDetector().detect()
    assert info.installed is True
    assert info.path == str(kicad_exe)
    assert info.version == "10.0.5"


def test_kicad_detector_missing_from_all_roots(monkeypatch, tmp_path):
    """When KiCad is not installed in any location, detector must return installed=False."""
    monkeypatch.setattr("shutil.which", lambda name: None)
    monkeypatch.setattr("sys.platform", "win32")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "empty1"))
    monkeypatch.setenv("ProgramFiles", str(tmp_path / "empty2"))

    info = KiCadDetector().detect()
    assert info.installed is False
    assert info.path is None
