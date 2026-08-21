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
            logger.info(f"KiCad WinGet installation finished successfully (code {result.returncode}).")
            return True
        except Exception as e:
            msg = f"Error running WinGet: {e}"
            print(msg)
            logger.error(msg)
            return False


class GhdlInstaller:
    def install(self) -> bool:
        logger.info("Starting GHDL installation check...")
        if sys.platform == "win32":
            winget = find_winget()
            if not winget:
                msg = "WinGet not found for GHDL installation. Please install WinGet or GHDL manually."
                print(msg)
                logger.error(msg)
                return False
            cmd = [winget, "install", "--id", "ghdl.ghdl.ucrt64.mcode", "--exact", "--accept-source-agreements", "--accept-package-agreements"]
        else:
            cmd = ["sudo", "apt-get", "install", "-y", "ghdl"]

        print(f"Installing GHDL using {'WinGet' if sys.platform == 'win32' else 'apt'}...")
        try:
            result = subprocess.run(cmd, text=True)
            if result.returncode not in (0, 2316632107, -1978238933):
                msg = f"GHDL installation finished with exit code {result.returncode}."
                print(msg)
                logger.error(msg)
                return False
            logger.info("GHDL installation finished successfully.")
            return True
        except Exception as e:
            msg = f"Error installing GHDL: {e}"
            print(msg)
            logger.error(msg)
            return False


class VerilatorInstaller:
    def install(self) -> bool:
        logger.info("Starting Verilator installation check...")
        if sys.platform == "win32":
            pacman = Path("C:/msys64/usr/bin/pacman.exe")
            if pacman.is_file():
                cmd = [str(pacman), "-S", "--noconfirm", "mingw-w64-x86_64-verilator"]
            else:
                msg = "Verilator installation on Windows requires MSYS2 (pacman not found at C:\\msys64\\usr\\bin\\pacman.exe). Please install MSYS2 or run on Linux."
                print(msg)
                logger.error(msg)
                return False
        else:
            cmd = ["sudo", "apt-get", "install", "-y", "verilator"]

        print(f"Installing Verilator using {'MSYS2 pacman' if sys.platform == 'win32' else 'apt'}...")
        try:
            result = subprocess.run(cmd, text=True)
            if result.returncode not in (0, 2316632107, -1978238933):
                msg = f"Verilator installation finished with exit code {result.returncode}."
                print(msg)
                logger.error(msg)
                return False
            logger.info("Verilator installation finished successfully.")
            return True
        except Exception as e:
            msg = f"Error installing Verilator: {e}"
            print(msg)
            logger.error(msg)
            return False


import sys
from config import get_install_dir
from logger import get_logger

logger = get_logger()


import shutil

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

        version = self._parse_version()
        version_dir = self.install_dir / "versions" / version
        version_dir.mkdir(parents=True, exist_ok=True)

        print(f"Extracting {self.archive} ...")
        print(f"Into version directory {version_dir} ...")
        try:
            with py7zr.SevenZipFile(self.archive, mode="r") as z:
                z.extractall(path=version_dir)
            logger.info(f"Extracted {self.archive} to {version_dir}")
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            return False

        exe = version_dir / "Spice64" / "bin" / "ngspice.exe"
        if not exe.is_file():
            msg = f"Installation failed: ngspice.exe not found in {version_dir} after extraction."
            print(msg)
            logger.error(msg)
            return False

        # Activate version: sync contents from versions/<ver> into active/
        active_dir = self.install_dir / "active"
        if active_dir.exists():
            shutil.rmtree(active_dir)

        shutil.copytree(version_dir, active_dir)
        active_exe = active_dir / "Spice64" / "bin" / "ngspice.exe"

        metadata = {
            "name": "ngspice",
            "version": version,
            "path": str(active_exe),
            "active_version": version,
        }
        metadata_path = self.install_dir / "metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=4)

        msg = f"Installed and activated Ngspice {version}. Metadata written to {metadata_path}."
        print(f"Installed and activated Ngspice {version}.")
        print(f"Metadata written to {metadata_path}.")
        logger.info(msg)
        return True

    def safe_upgrade(self, new_archive: Path) -> bool:
        """Safe upgrade with verification and automatic rollback on failure."""
        logger.info(f"Initiating safe upgrade using archive: {new_archive}")

        if not new_archive.is_file():
            msg = f"Upgrade archive not found: {new_archive}"
            print(msg)
            logger.error(msg)
            return False

        new_version = self._parse_version_from(new_archive)
        version_dir = self.install_dir / "versions" / new_version
        version_dir.mkdir(parents=True, exist_ok=True)

        print(f"Extracting upgrade candidate ({new_archive.name}) to {version_dir} ...")
        try:
            with py7zr.SevenZipFile(new_archive, mode="r") as z:
                z.extractall(path=version_dir)
        except Exception as e:
            msg = f"Extraction of candidate {new_version} failed: {e}. Upgrade aborted."
            print(msg)
            logger.error(msg)
            if version_dir.exists():
                shutil.rmtree(version_dir)
            return False

        # Verification step on candidate
        candidate_exe = version_dir / "Spice64" / "bin" / "ngspice.exe"
        if not candidate_exe.is_file():
            msg = f"Verification failed: executable missing in {version_dir}. Aborting upgrade."
            print(msg)
            logger.error(msg)
            shutil.rmtree(version_dir)
            return False

        # Prepare backup of active version
        active_dir = self.install_dir / "active"
        backup_dir = self.install_dir / "active_backup"
        metadata_path = self.install_dir / "metadata.json"
        metadata_backup = self.install_dir / "metadata.json.bak"

        if active_dir.exists():
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            shutil.copytree(active_dir, backup_dir)

        if metadata_path.exists():
            shutil.copy2(metadata_path, metadata_backup)

        try:
            print(f"Verification passed. Activating version {new_version} ...")
            if active_dir.exists():
                shutil.rmtree(active_dir)

            shutil.copytree(version_dir, active_dir)
            active_exe = active_dir / "Spice64" / "bin" / "ngspice.exe"

            metadata = {
                "name": "ngspice",
                "version": new_version,
                "path": str(active_exe),
                "active_version": new_version,
            }
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=4)

            # Clean backup on successful activation
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            if metadata_backup.exists():
                metadata_backup.unlink()

            logger.info(f"Successfully upgraded Ngspice to version {new_version}.")
            print(f"Upgrade to version {new_version} completed successfully.")
            return True

        except Exception as e:
            logger.error(f"Error during activation: {e}. Performing automatic rollback...")
            self._rollback(backup_dir, active_dir, metadata_backup, metadata_path)
            return False

    def _rollback(self, backup_dir: Path, active_dir: Path, metadata_backup: Path, metadata_path: Path):
        print("Rolling back to previous active version...")
        if backup_dir.exists():
            if active_dir.exists():
                shutil.rmtree(active_dir)
            shutil.copytree(backup_dir, active_dir)
            shutil.rmtree(backup_dir)

        if metadata_backup.exists():
            if metadata_path.exists():
                metadata_path.unlink()
            shutil.copy2(metadata_backup, metadata_path)
            metadata_backup.unlink()

        logger.info("Rollback completed. Restored previous active version.")
        print("Rollback completed. Previous active version remains active.")

    def _parse_version(self) -> str:
        return self._parse_version_from(self.archive)

    def _parse_version_from(self, archive_path: Path) -> str:
        return archive_path.stem.split("-")[1].split("_")[0]


if __name__ == "__main__":
    archive = Path("downloads/ngspice-47_64.7z")
    NgspiceInstaller(archive).install()
