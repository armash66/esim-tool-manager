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
    monkeypatch.setattr("installer.find_winget", lambda: None)
    installer = KiCadInstaller()
    assert installer.install() is False


def test_ghdl_installer_winget_missing(monkeypatch):
    monkeypatch.setattr("installer.find_winget", lambda: None)
    installer = GhdlInstaller()
    assert installer.install() is False


def test_verilator_installer_winget_missing(monkeypatch):
    monkeypatch.setattr("installer.find_winget", lambda: None)
    installer = VerilatorInstaller()
    assert installer.install() is False
