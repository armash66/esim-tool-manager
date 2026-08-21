import py7zr
from pathlib import Path

archive = Path("downloads/ngspice-47_64.7z")
output  = Path("downloads/ngspice-47_64")

print(f"Extracting {archive} ...")

with py7zr.SevenZipFile(archive, mode="r") as z:
    z.extractall(path=output)

print(f"Done. Contents of {output}/:")
for item in output.iterdir():
    print(" ", item.name)
