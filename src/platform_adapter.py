import os
import shutil
import sys
from pathlib import Path


class BasePlatformAdapter:
    def get_name(self) -> str:
        raise NotImplementedError

    def find_package_manager(self) -> str | None:
        raise NotImplementedError

    def get_default_install_dir(self) -> Path:
        return Path.home() / ".esim-tools"

    def format_path_instructions(self, bin_paths: list[str]) -> str:
        raise NotImplementedError


class WindowsAdapter(BasePlatformAdapter):
    def get_name(self) -> str:
        return "Windows"

    def find_package_manager(self) -> str | None:
        path = shutil.which("winget")
        if path:
            return path
        fallback = Path.home() / "AppData" / "Local" / "Microsoft" / "WindowsApps" / "winget.exe"
        if fallback.is_file():
            return str(fallback)
        return None

    def format_path_instructions(self, bin_paths: list[str]) -> str:
        ps_path = ";".join(bin_paths)
        return (
            "Environment PATH Configuration Instructions (Windows):\n"
            "  PowerShell:\n"
            f'    $env:Path += ";{ps_path}"\n'
            "  Command Prompt:\n"
            f'    set PATH=%PATH%;{ps_path}'
        )


class LinuxAdapter(BasePlatformAdapter):
    def get_name(self) -> str:
        return "Linux"

    def find_package_manager(self) -> str | None:
        return shutil.which("apt-get") or shutil.which("apt") or shutil.which("dnf") or shutil.which("pacman")

    def format_path_instructions(self, bin_paths: list[str]) -> str:
        bash_path = ":".join(bin_paths)
        return (
            "Environment PATH Configuration Instructions (Linux/POSIX):\n"
            "  Bash / Zsh:\n"
            f'    export PATH="$PATH:{bash_path}"'
        )


def get_platform_adapter() -> BasePlatformAdapter:
    if sys.platform == "win32":
        return WindowsAdapter()
    else:
        return LinuxAdapter()
