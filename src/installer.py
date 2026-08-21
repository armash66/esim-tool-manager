import json
import shutil
import subprocess
import py7zr
from pathlib import Path


def find_winget() -> str | None:
    """Find winget on PATH or in standard WindowsApps location."""
    path = shutil.which("winget")
    if path:
        return path

    fallback = Path.home() / "AppData" / "Local" / "Microsoft" / "WindowsApps" / "winget.exe"
    if fallback.is_file():
        return str(fallback)

    return None


class KiCadInstaller:
    def install(self) -> bool:
        logger.info("Starting KiCad installation check via WinGet...")
        winget = find_winget()
        if not winget:
            msg = "WinGet not found. Please install/enable App Installer."
            print(msg)
            logger.error(msg)
            return False

        print("Checking WinGet...")
        print("Installing KiCad via WinGet...")
        cmd = [
            winget,
            "install",
            "--id", "KiCad.KiCad",
            "--exact",
            "--accept-source-agreements",
            "--accept-package-agreements"
        ]

        try:
            result = subprocess.run(cmd, text=True)
            # 0 = success, 2316632107 / 0x8A15002B = already installed & no upgrade available
            if result.returncode not in (0, 2316632107, -1978238933):
                msg = f"WinGet returned exit code {result.returncode}."
                print(msg)
                logger.error(msg)
                return False
            logger.info(f"KiCad WinGet installation finished successfully (code {result.returncode}).")
            return True
        except Exception as e:
            msg = f"Error running WinGet: {e}"
            print(msg)
            logger.error(msg)
            return False


from config import get_install_dir
from logger import get_logger

logger = get_logger()


class NgspiceInstaller:
    def __init__(self, archive: Path):
        self.archive = archive
        self.install_dir = get_install_dir() / "ngspice"

    def install(self) -> bool:
        logger.info(f"Starting Ngspice installation from {self.archive}")
        if not self.archive.is_file():
            msg = f"Archive not found: {self.archive}"
            print(msg)
            logger.error(msg)
            return False

        self.install_dir.mkdir(parents=True, exist_ok=True)

        print(f"Extracting {self.archive} ...")
        print(f"Into       {self.install_dir} ...")
        try:
            with py7zr.SevenZipFile(self.archive, mode="r") as z:
                z.extractall(path=self.install_dir)
            logger.info(f"Extracted {self.archive} to {self.install_dir}")
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            return False

        exe = self.install_dir / "Spice64" / "bin" / "ngspice.exe"
        if not exe.is_file():
            msg = "Installation failed: ngspice.exe not found after extraction."
            print(msg)
            logger.error(msg)
            return False

        version = self._parse_version()
        metadata = {
            "name": "ngspice",
            "version": version,
            "path": str(exe),
        }
        metadata_path = self.install_dir / "metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=4)

        msg = f"Installed Ngspice {version}. Metadata written to {metadata_path}."
        print(f"Installed Ngspice {version}.")
        print(f"Metadata written to {metadata_path}.")
        logger.info(msg)
        return True

    def _parse_version(self) -> str:
        # ngspice-47_64.7z  →  stem = "ngspice-47_64"
        #   → split("-")[1] = "47_64"
        #   → split("_")[0] = "47"
        return self.archive.stem.split("-")[1].split("_")[0]


if __name__ == "__main__":
    archive = Path("downloads/ngspice-47_64.7z")
    NgspiceInstaller(archive).install()
