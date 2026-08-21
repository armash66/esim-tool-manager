import json
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from manifest import OperationResult, ToolchainPlanner, ToolchainManager, PlannedAction
from detector import ToolInfo


def test_operation_result_serialization():
    res = OperationResult(
        tool="kicad",
        action="install",
        success=True,
        old_version=None,
        new_version="10.0.5",
        message="Installation verified"
    )
    d = res.to_dict()
    assert d["tool"] == "kicad"
    assert d["success"] is True

    js = res.to_json()
    assert '"tool": "kicad"' in js
    assert '"new_version": "10.0.5"' in js


def test_planner_all_installed_and_matching(monkeypatch):
    monkeypatch.setattr(
        "detector.KiCadDetector.detect",
        lambda self: ToolInfo(name="KiCad", installed=True, path="kicad.exe", version="10.0.5"),
    )
    monkeypatch.setattr(
        "detector.NgspiceDetector.detect",
        lambda self: ToolInfo(name="Ngspice", installed=True, path="ngspice.exe", version="47"),
    )
    monkeypatch.setattr(
        "detector.GhdlDetector.detect",
        lambda self: ToolInfo(name="GHDL", installed=True, path="ghdl.exe", version="6.0.0"),
    )
    monkeypatch.setattr(
        "detector.VerilatorDetector.detect",
        lambda self: ToolInfo(name="Verilator", installed=True, path="verilator.exe", version="5.040"),
    )

    manifest_data = {
        "schema_version": 1,
        "tools": {
            "kicad": {"version": "10.0.5"},
            "ngspice": {"version": "47"},
            "ghdl": {"version": "6.0.0"},
            "verilator": {"version": "5.040"},
        }
    }

    planner = ToolchainPlanner()
    plans = planner.plan(manifest_data)
    assert len(plans) == 4
    for p in plans:
        assert p.action == "NO_ACTION"


def test_planner_missing_and_mismatch(monkeypatch):
    monkeypatch.setattr(
        "detector.KiCadDetector.detect",
        lambda self: ToolInfo(name="KiCad", installed=False, path=None, version=None),
    )
    monkeypatch.setattr(
        "detector.NgspiceDetector.detect",
        lambda self: ToolInfo(name="Ngspice", installed=True, path="ngspice.exe", version="46"),
    )
    monkeypatch.setattr(
        "detector.GhdlDetector.detect",
        lambda self: ToolInfo(name="GHDL", installed=True, path="ghdl.exe", version="6.0.0"),
    )
    monkeypatch.setattr(
        "detector.VerilatorDetector.detect",
        lambda self: ToolInfo(name="Verilator", installed=True, path="verilator.exe", version="5.050"),
    )

    manifest_data = {
        "schema_version": 1,
        "tools": {
            "kicad": {"version": "10.0.5"},
            "ngspice": {"version": "47"},
            "ghdl": {"version": "6.0.0"},
            "verilator": {"version": "5.040"},
        }
    }

    planner = ToolchainPlanner()
    plans = {p.tool: p for p in planner.plan(manifest_data)}

    assert plans["kicad"].action == "INSTALL"
    assert plans["ngspice"].action == "UPDATE"  # 46 < 47
    assert plans["ghdl"].action == "NO_ACTION"  # 6.0.0 == 6.0.0
    assert plans["verilator"].action == "MISMATCH"  # 5.050 > 5.040


def test_snapshot_creation(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "detector.KiCadDetector.detect",
        lambda self: ToolInfo(name="KiCad", installed=True, path="C:\\kicad\\kicad-cli.exe", version="10.0.5"),
    )
    monkeypatch.setattr(
        "detector.NgspiceDetector.detect",
        lambda self: ToolInfo(name="Ngspice", installed=False, path=None, version=None),
    )
    monkeypatch.setattr(
        "detector.GhdlDetector.detect",
        lambda self: ToolInfo(name="GHDL", installed=False, path=None, version=None),
    )
    monkeypatch.setattr(
        "detector.VerilatorDetector.detect",
        lambda self: ToolInfo(name="Verilator", installed=False, path=None, version=None),
    )

    tm = ToolchainManager()
    out_file = tmp_path / "esim-toolchain.json"
    manifest = tm.snapshot(out_file)

    assert out_file.is_file()
    assert manifest["tools"]["kicad"]["installed"] is True
    assert manifest["tools"]["kicad"]["version"] == "10.0.5"
    assert manifest["tools"]["ngspice"]["installed"] is False


def test_verify_manifest(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "detector.KiCadDetector.detect",
        lambda self: ToolInfo(name="KiCad", installed=True, path="C:\\kicad\\kicad-cli.exe", version="10.0.5"),
    )
    monkeypatch.setattr(
        "detector.NgspiceDetector.detect",
        lambda self: ToolInfo(name="Ngspice", installed=False, path=None, version=None),
    )
    monkeypatch.setattr(
        "detector.GhdlDetector.detect",
        lambda self: ToolInfo(name="GHDL", installed=True, path="ghdl.exe", version="6.0.0"),
    )
    monkeypatch.setattr(
        "detector.VerilatorDetector.detect",
        lambda self: ToolInfo(name="Verilator", installed=True, path="verilator.exe", version="5.040"),
    )

    m_file = tmp_path / "test-manifest.json"
    m_file.write_text(json.dumps({
        "schema_version": 1,
        "tools": {
            "kicad": {"version": "10.0.5"},
            "ngspice": {"version": "47"},
            "ghdl": {"version": "6.0.0"},
            "verilator": {"version": "5.040"}
        }
    }))

    tm = ToolchainManager()
    results = tm.verify_manifest(m_file)
    res_dict = {r.tool: r for r in results}

    assert res_dict["kicad"].success is True
    assert res_dict["ngspice"].success is False  # Missing
    assert res_dict["ghdl"].success is True
    assert res_dict["verilator"].success is True


def test_dry_run_sync_makes_no_changes(monkeypatch, tmp_path):
    install_called = []

    class MockInstaller:
        def install(self):
            install_called.append(True)
            return True

    import manifest
    monkeypatch.setattr(manifest, "get_installer", lambda t: MockInstaller())
    monkeypatch.setattr(
        "detector.KiCadDetector.detect",
        lambda self: ToolInfo(name="KiCad", installed=False, path=None, version=None),
    )
    monkeypatch.setattr(
        "detector.NgspiceDetector.detect",
        lambda self: ToolInfo(name="Ngspice", installed=False, path=None, version=None),
    )
    monkeypatch.setattr(
        "detector.GhdlDetector.detect",
        lambda self: ToolInfo(name="GHDL", installed=False, path=None, version=None),
    )
    monkeypatch.setattr(
        "detector.VerilatorDetector.detect",
        lambda self: ToolInfo(name="Verilator", installed=False, path=None, version=None),
    )

    m_file = tmp_path / "test-manifest.json"
    m_file.write_text(json.dumps({
        "schema_version": 1,
        "tools": {
            "kicad": {"version": "10.0.5"}
        }
    }))

    tm = ToolchainManager()
    results = tm.sync_manifest(m_file, dry_run=True)

    assert len(install_called) == 0, "Dry run must not invoke actual installers"
    assert results[0].action == "install"
    assert "[DRY-RUN]" in results[0].message
