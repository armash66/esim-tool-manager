from pathlib import Path
from detector import GhdlDetector, KiCadDetector, NgspiceDetector, VerilatorDetector
from installer import GhdlInstaller, KiCadInstaller, NgspiceInstaller, VerilatorInstaller
from updater import KiCadUpdater, NgspiceUpdater


def get_ngspice_installer():
    archive_path = Path("downloads/ngspice-47_64.7z")
    return NgspiceInstaller(archive_path)


TOOLS = {
    "kicad": {
        "name": "KiCad",
        "category": "core-tool",
        "detector": KiCadDetector,
        "installer": KiCadInstaller,
        "updater": KiCadUpdater,
    },
    "ngspice": {
        "name": "Ngspice",
        "category": "core-tool",
        "detector": NgspiceDetector,
        "installer": get_ngspice_installer,
        "updater": NgspiceUpdater,
    },
    "ghdl": {
        "name": "GHDL",
        "category": "core-tool",
        "detector": GhdlDetector,
        "installer": GhdlInstaller,
        "updater": None,
    },
    "verilator": {
        "name": "Verilator",
        "category": "core-tool",
        "detector": VerilatorDetector,
        "installer": VerilatorInstaller,
        "updater": None,
    },
}


def get_detector(tool_name: str):
    tool = TOOLS.get(tool_name.lower())
    if tool and tool["detector"]:
        detector_cls = tool["detector"]
        return detector_cls()
    return None


def get_installer(tool_name: str):
    tool = TOOLS.get(tool_name.lower())
    if tool and tool["installer"]:
        installer_factory = tool["installer"]
        return installer_factory()
    return None


def get_updater(tool_name: str):
    tool = TOOLS.get(tool_name.lower())
    if tool and tool["updater"]:
        updater_cls = tool["updater"]
        return updater_cls()
    return None


def list_tools():
    return list(TOOLS.keys())


def get_all_detectors():
    detectors = []
    for tool_name, info in TOOLS.items():
        if info["detector"]:
            detectors.append(info["detector"]())
    return detectors
