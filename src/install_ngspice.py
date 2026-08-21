import py7zr
from pathlib import Path

archive     = Path("downloads/ngspice-47_64.7z")
install_dir = Path.home() / ".esim-tools" / "ngspice"

install_dir.mkdir(parents=True, exist_ok=True)

print(f"Extracting {archive} ...")
print(f"Into       {install_dir} ...")

with py7zr.SevenZipFile(archive, mode="r") as z:
    z.extractall(path=install_dir)

print("Done. Contents:")
for item in install_dir.iterdir():
    print(" ", item.name)
