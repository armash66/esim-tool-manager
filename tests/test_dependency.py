import json
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dependency import DependencyChecker, DependencyState


def test_dependency_checker_installed(monkeypatch, tmp_path):
    install_dir = tmp_path / ".esim-tools"
    monkeypatch.setattr("dependency.get_install_dir", lambda: install_dir)
    monkeypatch.setattr("detector.get_install_dir", lambda: install_dir)

    exe = install_dir / "ngspice" / "Spice64" / "bin" / "ngspice.exe"
    exe.parent.mkdir(parents=True, exist_ok=True)
    exe.write_text("fake binary")

    metadata_file = install_dir / "ngspice" / "metadata.json"
    metadata_file.write_text(json.dumps({"name": "ngspice", "version": "47", "path": str(exe)}))

    checker = DependencyChecker()
    status = checker.check_tool("ngspice")
    assert status.state == DependencyState.INSTALLED
    assert status.version == "47"


def test_dependency_checker_broken(monkeypatch, tmp_path):
    install_dir = tmp_path / ".esim-tools"
    monkeypatch.setattr("dependency.get_install_dir", lambda: install_dir)
    monkeypatch.setattr("detector.get_install_dir", lambda: install_dir)

    # Metadata exists pointing to missing executable
    missing_exe = install_dir / "ngspice" / "Spice64" / "bin" / "nonexistent.exe"
    metadata_file = install_dir / "ngspice" / "metadata.json"
    metadata_file.parent.mkdir(parents=True, exist_ok=True)
    metadata_file.write_text(json.dumps({"name": "ngspice", "version": "47", "path": str(missing_exe)}))

    checker = DependencyChecker()
    status = checker.check_tool("ngspice")
    assert status.state == DependencyState.BROKEN


def test_dependency_checker_environment(tmp_path, monkeypatch):
    install_dir = tmp_path / ".esim-tools"
    install_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr("dependency.get_install_dir", lambda: install_dir)

    checker = DependencyChecker()
    env = checker.check_environment()
    assert env["install_dir_exists"] is True
    assert env["config_valid"] is True
