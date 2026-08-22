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
    def __init__(self):
        self.last_error: str | None = None

    def install(self) -> bool:
        self.last_error = None
        logger.info("Starting KiCad installation via WinGet...")

        # Pre-check: if already installed and verified, skip
        from detector import KiCadDetector
        pre_info = KiCadDetector().detect()
        if pre_info.installed:
            logger.info(f"KiCad already installed: {pre_info.version} at {pre_info.path}")
            print(f"KiCad is already installed ({pre_info.version}).")
            return True

        winget = find_winget()
        if not winget:
            msg = "Required prerequisite WinGet was not found. Please install/enable App Installer."
            self.last_error = msg
            print(msg)
            logger.error(msg)
            return False

        # Use --scope user --force to handle stale WinGet registrations
        # and install to per-user location without requiring elevation
        if sys.platform == "win32":
            cmd = [
                winget, "install", "--id", "KiCad.KiCad", "--exact",
                "--scope", "user", "--force",
                "--accept-source-agreements", "--accept-package-agreements"
            ]
        else:
            cmd = [
                winget, "install", "--id", "KiCad.KiCad", "--exact",
                "--accept-source-agreements", "--accept-package-agreements"
            ]

        print("Installing KiCad via WinGet...")
        try:
            result = subprocess.run(cmd, text=True, capture_output=True)
            logger.info(f"WinGet exit code: {result.returncode}")
            if result.stdout:
                logger.info(f"WinGet stdout: {result.stdout.strip()}")
            if result.stderr:
                logger.warning(f"WinGet stderr: {result.stderr.strip()}")
            if result.returncode not in (0, 2316632107, -1978238933):
                self.last_error = f"WinGet installer exited with code {result.returncode}."
        except Exception as e:
            self.last_error = f"Installer execution error: {e}"
            logger.error(f"Error running WinGet: {e}")
            return False

        # Verify installation via detector — never trust exit code alone
        info = KiCadDetector().detect()
        if info.installed:
            logger.info(f"KiCad installation verified: {info.version} at {info.path}")
            return True
        else:
            if not self.last_error:
                self.last_error = "Installation completed, but KiCad executable (kicad-cli.exe) could not be verified on disk."
            logger.error("WinGet finished but KiCadDetector could not find kicad-cli.exe.")
            return False

    def uninstall(self) -> bool:
        logger.info("Starting KiCad uninstallation via WinGet...")
        if sys.platform == "win32":
            winget = find_winget()
            if not winget:
                logger.error("WinGet not found for KiCad uninstall.")
                return False

            print("Uninstalling KiCad via WinGet...")
            try:
                subprocess.run(
                    [winget, "uninstall", "--id", "KiCad.KiCad", "--exact", "--accept-source-agreements"],
                    text=True
                )
            except Exception as e:
                logger.error(f"WinGet uninstall error: {e}")

            # Clean up leftover directories in both per-user and system-wide locations
            from detector import KiCadDetector
            for kicad_base in KiCadDetector._get_windows_roots():
                if kicad_base.is_dir():
                    try:
                        shutil.rmtree(kicad_base, ignore_errors=True)
                        logger.info(f"Cleaned leftover KiCad directory: {kicad_base}")
                    except Exception as e:
                        logger.warning(f"Could not clean KiCad directory {kicad_base}: {e}")

        from detector import KiCadDetector
        info = KiCadDetector().detect()
        if not info.installed:
            logger.info("KiCad uninstalled and verified successfully.")
            return True
        else:
            logger.error("KiCad executable was still detected after uninstallation attempt.")
            return False


class GhdlInstaller:
    def __init__(self):
        self.last_error: str | None = None

    def install(self) -> bool:
        self.last_error = None
        logger.info("Starting GHDL installation check...")
        if sys.platform == "win32":
            winget = find_winget()
            if not winget:
                msg = "Required prerequisite WinGet was not found. Please install WinGet."
                self.last_error = msg
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
                msg = f"GHDL installer exited with code {result.returncode}."
                self.last_error = msg
                print(msg)
                logger.error(msg)
                return False
        except Exception as e:
            msg = f"Error installing GHDL: {e}"
            self.last_error = msg
            print(msg)
            logger.error(msg)
            return False

        from detector import GhdlDetector
        info = GhdlDetector().detect()
        if info.installed:
            logger.info("GHDL installation finished and verified successfully.")
            return True
        else:
            self.last_error = "Installation completed, but executable ghdl.exe could not be verified on disk."
            logger.error(self.last_error)
            return False

    def uninstall(self) -> bool:
        logger.info("Starting GHDL uninstallation...")
        if sys.platform == "win32":
            winget = find_winget()
            if not winget:
                return False
            cmd = [winget, "uninstall", "--id", "ghdl.ghdl.ucrt64.mcode", "--exact", "--accept-source-agreements"]
        else:
            cmd = ["sudo", "apt-get", "remove", "-y", "ghdl"]

        print(f"Uninstalling GHDL using {'WinGet' if sys.platform == 'win32' else 'apt'}...")
        try:
            subprocess.run(cmd, text=True)
            from detector import GhdlDetector
            info = GhdlDetector().detect()
            return not info.installed
        except Exception as e:
            logger.error(f"Error uninstalling GHDL: {e}")
            return False


class VerilatorInstaller:
    def __init__(self):
        self.last_error: str | None = None

    def install(self) -> bool:
        self.last_error = None
        logger.info("Starting Verilator installation check...")
        if sys.platform == "win32":
            pacman = Path("C:/msys64/usr/bin/pacman.exe")
            if pacman.is_file():
                cmd = [str(pacman), "-S", "--noconfirm", "mingw-w64-x86_64-verilator"]
            else:
                msg = (
                    "Required prerequisite MSYS2 (pacman) was not found at C:\\msys64\\usr\\bin\\pacman.exe.\n\n"
                    "Recommendation: Install MSYS2 from https://www.msys2.org/\n"
                    "and ensure pacman is available, then retry the installation."
                )
                self.last_error = msg
                print("\n" + msg)
                logger.error(msg)
                return False
        else:
            cmd = ["sudo", "apt-get", "install", "-y", "verilator"]

        print(f"Installing Verilator using {'MSYS2 pacman' if sys.platform == 'win32' else 'apt'}...")
        try:
            result = subprocess.run(cmd, text=True)
            if result.returncode not in (0, 2316632107, -1978238933):
                msg = f"Verilator installer exited with code {result.returncode}."
                self.last_error = msg
                print(msg)
                logger.error(msg)
                return False
        except Exception as e:
            msg = f"Error installing Verilator: {e}"
            self.last_error = msg
            print(msg)
            logger.error(msg)
            return False

        from detector import VerilatorDetector
        info = VerilatorDetector().detect()
        if info.installed:
            logger.info("Verilator installation finished and verified successfully.")
            return True
        else:
            self.last_error = "Installation completed, but executable verilator could not be verified on disk."
            logger.error(self.last_error)
            return False

    def uninstall(self) -> bool:
        logger.info("Starting Verilator uninstallation...")
        if sys.platform == "win32":
            pacman = Path("C:/msys64/usr/bin/pacman.exe")
            if pacman.is_file():
                cmd = [str(pacman), "-R", "--noconfirm", "mingw-w64-x86_64-verilator"]
            else:
                return False
        else:
            cmd = ["sudo", "apt-get", "remove", "-y", "verilator"]

        print(f"Uninstalling Verilator using {'MSYS2 pacman' if sys.platform == 'win32' else 'apt'}...")
        try:
            subprocess.run(cmd, text=True)
            from detector import VerilatorDetector
            info = VerilatorDetector().detect()
            return not info.installed
        except Exception as e:
            logger.error(f"Error uninstalling Verilator: {e}")
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
        self.last_error: str | None = None

    def install(self) -> bool:
        self.last_error = None
        logger.info(f"Starting Ngspice installation from {self.archive}")
        if not self.archive.is_file():
            msg = f"Download archive not found at {self.archive}. Please verify network connection or download path."
            self.last_error = msg
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
            msg = f"Archive extraction failed: {e}"
            self.last_error = msg
            logger.error(msg)
            return False

        exe = version_dir / "Spice64" / "bin" / "ngspice.exe"
        if not exe.is_file():
            msg = f"Installation verification failed: ngspice.exe not found in {version_dir} after extraction."
            self.last_error = msg
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

    def uninstall(self) -> bool:
        logger.info(f"Uninstalling Ngspice from {self.install_dir}...")
        if self.install_dir.exists():
            shutil.rmtree(self.install_dir)
            logger.info("Ngspice directory removed successfully.")
            return True
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
