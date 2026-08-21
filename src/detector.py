import shutil
import subprocess
from pathlib import Path
from packaging.version import Version, InvalidVersion

# --- KiCad ---

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
    print("KiCad")
    print("Installed: No")
else:
    result = subprocess.run([path, "--version"], capture_output=True, text=True)

    print("KiCad")
    print("Installed: Yes")
    print("Path:     ", path)

    if result.returncode == 0:
        print("Version:  ", result.stdout.strip())
    else:
        print("Version:   (command failed, returncode:", result.returncode, ")")

print()

# --- Ngspice ---

path = shutil.which("ngspice")

if path is None:
    fallback = Path.home() / ".esim-tools" / "ngspice" / "Spice64" / "bin" / "ngspice.exe"
    if fallback.is_file():
        path = str(fallback)

if path is None:
    print("Ngspice")
    print("Installed: No")
else:
    result = subprocess.run([path, "--version"], capture_output=True, text=True)

    print("Ngspice")
    print("Installed: Yes")
    print("Path:     ", path)

    if result.returncode == 0:
        print("Version:  ", result.stdout.strip())
    else:
        print("Version:   (command failed, returncode:", result.returncode, ")")
