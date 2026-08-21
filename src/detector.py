import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from packaging.version import Version, InvalidVersion


@dataclass
class ToolInfo:
    name: str
    installed: bool
    path: str | None
    version: str | None


class KiCadDetector:
    def detect(self) -> ToolInfo:
        path = shutil.which("kicad-cli")

        if path is None:
            base = Path(r"C:\Program Files\KiCad")
            if base.is_dir():
                version_folders = []
                for folder in base.iterdir():
                    try:
                        ver = Version(folder.name)
                        version_folders.append((ver, folder))
                    except InvalidVersion:
                        pass

                version_folders.sort(reverse=True)

                for ver, folder in version_folders:
                    candidate = folder / "bin" / "kicad-cli.exe"
                    if candidate.is_file():
                        path = str(candidate)
                        break

        if path is None:
            return ToolInfo(name="KiCad", installed=False, path=None, version=None)

        result = subprocess.run([path, "--version"], capture_output=True, text=True)
        version = result.stdout.strip() if result.returncode == 0 else None
        return ToolInfo(name="KiCad", installed=True, path=path, version=version)


class NgspiceDetector:
    def detect(self) -> ToolInfo:
        path = shutil.which("ngspice")

        if path is None:
            fallback = Path.home() / ".esim-tools" / "ngspice" / "Spice64" / "bin" / "ngspice.exe"
            if fallback.is_file():
                path = str(fallback)

        if path is None:
            return ToolInfo(name="Ngspice", installed=False, path=None, version=None)

        # Don't execute ngspice.exe — it launches a GUI and produces no piped output.
        # Read version from metadata.json written by the installer instead.
        version = None
        metadata_path = Path.home() / ".esim-tools" / "ngspice" / "metadata.json"
        if metadata_path.is_file():
            with open(metadata_path) as f:
                version = json.load(f).get("version")

        return ToolInfo(name="Ngspice", installed=True, path=path, version=version)


def print_tool(info: ToolInfo) -> None:
    print(info.name)
    print("Installed:", "Yes" if info.installed else "No")
    if info.installed:
        print("Path:     ", info.path)
        print("Version:  ", info.version if info.version is not None else "(unavailable)")


if __name__ == "__main__":
    for detector in [KiCadDetector(), NgspiceDetector()]:
        print_tool(detector.detect())
        print()
