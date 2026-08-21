from pathlib import Path
from detector import KiCadDetector, NgspiceDetector
from installer import KiCadInstaller, NgspiceInstaller


def get_ngspice_installer():
    archive_path = Path("downloads/ngspice-47_64.7z")
    return NgspiceInstaller(archive_path)


TOOLS = {
    "kicad": {
        "name": "KiCad",
        "detector": KiCadDetector,
        "installer": KiCadInstaller,
    },
    "ngspice": {
        "name": "Ngspice",
        "detector": NgspiceDetector,
        "installer": get_ngspice_installer,
    },
}


def get_detector(tool_name: str):
    tool = TOOLS.get(tool_name.lower())
    if tool:
        detector_cls = tool["detector"]
        return detector_cls()
    return None


def get_installer(tool_name: str):
    tool = TOOLS.get(tool_name.lower())
    if tool:
        installer_factory = tool["installer"]
        return installer_factory()
    return None


def list_tools():
    return list(TOOLS.keys())


def get_all_detectors():
    return [get_detector(name) for name in list_tools()]
