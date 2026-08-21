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
