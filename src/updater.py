import subprocess
from pathlib import Path
from detector import KiCadDetector, NgspiceDetector
from installer import find_winget, KiCadInstaller, NgspiceInstaller
from packaging.version import Version, InvalidVersion


def get_kicad_latest_version() -> str | None:
    winget = find_winget()
    if not winget:
        return None

    try:
        cmd = [winget, "show", "--id", "KiCad.KiCad", "--exact"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if line.startswith("Version:"):
                    return line.split(":", 1)[1].strip()
    except Exception:
        pass
    return None


class KiCadUpdater:
    def check_update(self):
        detector = KiCadDetector()
        info = detector.detect()
        if not info.installed:
            return {"installed": False, "installed_version": None, "latest_version": None, "needs_update": False}

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
            "latest_version": latest or info.version,
            "needs_update": needs_update,
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
            return {"installed": False, "installed_version": None, "latest_version": None, "needs_update": False}

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
