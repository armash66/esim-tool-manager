import json
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from installer import NgspiceInstaller
from detector import NgspiceDetector


def test_safe_upgrade_and_rollback(monkeypatch, tmp_path):
    install_dir = tmp_path / ".esim-tools"
    monkeypatch.setattr("installer.get_install_dir", lambda: install_dir)
    monkeypatch.setattr("detector.get_install_dir", lambda: install_dir)

    # 1. Setup initial active version 47
    active_dir = install_dir / "ngspice" / "active"
    exe_47 = active_dir / "Spice64" / "bin" / "ngspice.exe"
    exe_47.parent.mkdir(parents=True, exist_ok=True)
    exe_47.write_text("binary v47")

    meta_file = install_dir / "ngspice" / "metadata.json"
    meta_file.write_text(json.dumps({"name": "ngspice", "version": "47", "path": str(exe_47)}))

    installer = NgspiceInstaller(tmp_path / "dummy.7z")

    # 2. Test upgrade with corrupted candidate (missing ngspice.exe in candidate extraction)
    fake_bad_archive = tmp_path / "ngspice-48_64.7z"
    fake_bad_archive.write_text("corrupted content")

    # Mock py7zr to simulate extraction of bad archive without executable
    class Dummy7z:
        def __init__(self, *args, **kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def extractall(self, path):
            Path(path).mkdir(parents=True, exist_ok=True)
            # Extracted without Spice64/bin/ngspice.exe

    monkeypatch.setattr("py7zr.SevenZipFile", Dummy7z)

    # Attempt upgrade — should fail verification and keep v47
    success = installer.safe_upgrade(fake_bad_archive)
    assert success is False

    # Verify detector still sees version 47 active
    detector = NgspiceDetector()
    info = detector.detect()
    assert info.installed is True
    assert info.version == "47"
    assert exe_47.is_file()
