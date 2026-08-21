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


from config import get_install_dir


class NgspiceDetector:
    def detect(self) -> ToolInfo:
        path = shutil.which("ngspice")

        if path is None:
            fallback = get_install_dir() / "ngspice" / "active" / "Spice64" / "bin" / "ngspice.exe"
            if not fallback.is_file():
                # Backward compatibility check for unversioned layout
                fallback = get_install_dir() / "ngspice" / "Spice64" / "bin" / "ngspice.exe"
            if fallback.is_file():
                path = str(fallback)

        if path is None:
            return ToolInfo(name="Ngspice", installed=False, path=None, version=None)

        # Don't execute ngspice.exe — it launches a GUI and produces no piped output.
        # Read version from metadata.json written by the installer instead.
        version = None
        metadata_path = get_install_dir() / "ngspice" / "metadata.json"
        if metadata_path.is_file():
            with open(metadata_path) as f:
                version = json.load(f).get("version")

        return ToolInfo(name="Ngspice", installed=True, path=path, version=version)


class GhdlDetector:
    def detect(self) -> ToolInfo:
        path = shutil.which("ghdl")

        if path is None:
            winget_pkg_dir = Path.home() / "AppData" / "Local" / "Microsoft" / "WinGet" / "Packages"
            if winget_pkg_dir.is_dir():
                matches = list(winget_pkg_dir.glob("ghdl*/**/ghdl.exe"))
                if matches:
                    path = str(matches[0])

        if path is None:
            winget_link = Path.home() / "AppData" / "Local" / "Microsoft" / "WinGet" / "Links" / "ghdl.exe"
            if winget_link.is_file():
                path = str(winget_link)

        if path is None:
            fallback = get_install_dir() / "ghdl" / "bin" / "ghdl.exe"
            if fallback.is_file():
                path = str(fallback)

        if path is None:
            return ToolInfo(name="GHDL", installed=False, path=None, version=None)

        result = subprocess.run([path, "--version"], capture_output=True, text=True)
        version = None
        if result.returncode == 0:
            # GHDL --version output first line: "GHDL 4.0.0-dev (3.0.0.r105.g749021b0) [GHDL mcode engine]"
            first_line = result.stdout.strip().splitlines()[0] if result.stdout.strip() else ""
            if first_line.startswith("GHDL "):
                version = first_line.split()[1]
            else:
                version = first_line

        return ToolInfo(name="GHDL", installed=True, path=path, version=version)


class VerilatorDetector:
    def detect(self) -> ToolInfo:
        path = shutil.which("verilator") or shutil.which("verilator_bin")

        if path is None:
            for exe_name in ("verilator.exe", "verilator_bin.exe"):
                fallback = Path.home() / ".esim-tools" / "verilator" / "bin" / exe_name
                if fallback.is_file():
                    path = str(fallback)
                    break

        if path is None:
            return ToolInfo(name="Verilator", installed=False, path=None, version=None)

        result = subprocess.run([path, "--version"], capture_output=True, text=True)
        version = None
        if result.returncode == 0:
            # Verilator --version output: "Verilator 5.020 2024-01-01 ..."
            first_line = result.stdout.strip().splitlines()[0] if result.stdout.strip() else ""
            parts = first_line.split()
            if len(parts) >= 2 and parts[0] == "Verilator":
                version = parts[1]
            else:
                version = first_line

        return ToolInfo(name="Verilator", installed=True, path=path, version=version)


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
