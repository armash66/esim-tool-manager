import shutil
import subprocess
from pathlib import Path

path = shutil.which("kicad-cli")

if path is None:
    fallback = Path(r"C:\Program Files\KiCad\10.0") / "bin" / "kicad-cli.exe"
    if fallback.is_file():
        path = str(fallback)

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
