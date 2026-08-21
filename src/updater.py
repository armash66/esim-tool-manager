import subprocess
from pathlib import Path
from detector import KiCadDetector, NgspiceDetector
from installer import find_winget, KiCadInstaller, NgspiceInstaller
from packaging.version import Version, InvalidVersion


def get_winget_latest_version(package_id: str) -> str | None:
    winget = find_winget()
    if not winget:
        return None

    try:
        cmd = [winget, "show", "--id", package_id, "--exact"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if line.startswith("Version:"):
                    return line.split(":", 1)[1].strip()
    except Exception:
        pass
    return None


def get_kicad_latest_version() -> str | None:
    return get_winget_latest_version("KiCad.KiCad")


class KiCadUpdater:
    def check_update(self):
        detector = KiCadDetector()
        info = detector.detect()
        if not info.installed:
            return {"installed": False, "installed_version": None, "latest_version": None, "needs_update": False, "error": None}

        latest = get_kicad_latest_version()
        if info.version and latest:
            try:
                needs_update = Version(latest) > Version(info.version)
            except InvalidVersion:
                needs_update = (latest != info.version)
        else:
            needs_update = False

        return {
            "installed": True,
            "installed_version": info.version,
            "latest_version": latest,
            "needs_update": needs_update,
            "error": None if latest else "Unable to determine latest version",
        }

    def update(self) -> bool:
        status = self.check_update()
        if not status["installed"]:
            print("KiCad is not installed. Use 'install kicad' first.")
            return False

        if not status["needs_update"]:
            print(f"KiCad is already up to date (version {status['installed_version']}).")
            return True

        print(f"Updating KiCad from {status['installed_version']} to {status['latest_version']}...")
        return KiCadInstaller().install()


class NgspiceUpdater:
    def check_update(self):
        detector = NgspiceDetector()
        info = detector.detect()
        if not info.installed:
            return {"installed": False, "installed_version": None, "latest_version": None, "needs_update": False, "error": None}

        # Available local release version
        latest = "47"
        needs_update = False
        if info.version and latest:
            try:
                needs_update = Version(latest) > Version(info.version)
            except InvalidVersion:
                needs_update = (latest != info.version)

        return {
            "installed": True,
            "installed_version": info.version,
            "latest_version": latest,
            "needs_update": needs_update,
            "error": None,
        }

    def update(self) -> bool:
        status = self.check_update()
        if not status["installed"]:
            print("Ngspice is not installed. Use 'install ngspice' first.")
            return False

        if not status["needs_update"]:
            print(f"Ngspice is already up to date (version {status['installed_version']}).")
            return True

        print(f"Updating Ngspice from {status['installed_version']} to {status['latest_version']}...")
        archive_path = Path("downloads/ngspice-47_64.7z")
        return NgspiceInstaller(archive_path).install()


class GhdlUpdater:
    def check_update(self):
        from detector import GhdlDetector
        detector = GhdlDetector()
        info = detector.detect()
        if not info.installed:
            return {"installed": False, "installed_version": None, "latest_version": None, "needs_update": False, "error": None}

        latest = get_winget_latest_version("ghdl.ghdl.ucrt64.mcode")
        if info.version and latest:
            try:
                needs_update = Version(latest) > Version(info.version)
            except InvalidVersion:
                needs_update = (latest != info.version)
        else:
            needs_update = False

        return {
            "installed": True,
            "installed_version": info.version,
            "latest_version": latest,
            "needs_update": needs_update,
            "error": None if latest else "Unable to determine latest version",
        }

    def update(self) -> bool:
        from installer import GhdlInstaller
        status = self.check_update()
        if not status["installed"]:
            print("GHDL is not installed. Use 'install ghdl' first.")
            return False

        if not status["needs_update"]:
            print(f"GHDL is already up to date (version {status['installed_version']}).")
            return True

        print(f"Updating GHDL from {status['installed_version']} to {status['latest_version']}...")
        return GhdlInstaller().install()


class VerilatorUpdater:
    def check_update(self):
        from detector import VerilatorDetector
        detector = VerilatorDetector()
        info = detector.detect()
        if not info.installed:
            return {"installed": False, "installed_version": None, "latest_version": None, "needs_update": False, "error": None}

        # Check MSYS2 pacman or winget or fallback
        latest = get_winget_latest_version("verilator.verilator")
        if not latest:
            # Fallback check via pacman if msys2 exists
            pacman = shutil.which("pacman")
            if pacman:
                try:
                    res = subprocess.run([pacman, "-Si", "mingw-w64-x86_64-verilator"], capture_output=True, text=True, timeout=10)
                    if res.returncode == 0:
                        for line in res.stdout.splitlines():
                            if line.startswith("Version"):
                                latest = line.split(":", 1)[1].strip().split("-")[0]
                                break
                except Exception:
                    pass

        if info.version and latest:
            try:
                needs_update = Version(latest) > Version(info.version)
            except InvalidVersion:
                needs_update = (latest != info.version)
        else:
            needs_update = False

        return {
            "installed": True,
            "installed_version": info.version,
            "latest_version": latest,
            "needs_update": needs_update,
            "error": None if latest else "Unable to determine latest version",
        }

    def update(self) -> bool:
        from installer import VerilatorInstaller
        status = self.check_update()
        if not status["installed"]:
            print("Verilator is not installed. Use 'install verilator' first.")
            return False

        if not status["needs_update"]:
            print(f"Verilator is already up to date (version {status['installed_version']}).")
            return True

        print(f"Updating Verilator from {status['installed_version']} to {status['latest_version']}...")
        return VerilatorInstaller().install()

