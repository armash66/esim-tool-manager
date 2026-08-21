from pathlib import Path
from detector import GhdlDetector, KiCadDetector, NgspiceDetector, VerilatorDetector
from installer import KiCadInstaller, NgspiceInstaller


def get_ngspice_installer():
    archive_path = Path("downloads/ngspice-47_64.7z")
    return NgspiceInstaller(archive_path)


TOOLS = {
    "kicad": {
        "name": "KiCad",
        "category": "core-tool",
        "detector": KiCadDetector,
        "installer": KiCadInstaller,
    },
    "ngspice": {
        "name": "Ngspice",
        "category": "core-tool",
        "detector": NgspiceDetector,
        "installer": get_ngspice_installer,
    },
    "ghdl": {
        "name": "GHDL",
        "category": "core-tool",
        "detector": GhdlDetector,
        "installer": None,
    },
    "verilator": {
        "name": "Verilator",
        "category": "core-tool",
        "detector": VerilatorDetector,
        "installer": None,
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


def list_tools():
    return list(TOOLS.keys())


def get_all_detectors():
    detectors = []
    for tool_name, info in TOOLS.items():
        if info["detector"]:
            detectors.append(info["detector"]())
    return detectors
