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
