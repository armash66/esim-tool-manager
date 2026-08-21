import json
import py7zr
from pathlib import Path


class NgspiceInstaller:
    def __init__(self, archive: Path):
        self.archive = archive
        self.install_dir = Path.home() / ".esim-tools" / "ngspice"

    def install(self) -> bool:
        if not self.archive.is_file():
            print(f"Archive not found: {self.archive}")
            return False

        self.install_dir.mkdir(parents=True, exist_ok=True)

        print(f"Extracting {self.archive} ...")
        print(f"Into       {self.install_dir} ...")
        with py7zr.SevenZipFile(self.archive, mode="r") as z:
            z.extractall(path=self.install_dir)

        exe = self.install_dir / "Spice64" / "bin" / "ngspice.exe"
        if not exe.is_file():
            print("Installation failed: ngspice.exe not found after extraction.")
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

        print(f"Installed Ngspice {version}.")
        print(f"Metadata written to {metadata_path}.")
        return True

    def _parse_version(self) -> str:
        # ngspice-47_64.7z  →  stem = "ngspice-47_64"
        #   → split("-")[1] = "47_64"
        #   → split("_")[0] = "47"
        return self.archive.stem.split("-")[1].split("_")[0]


if __name__ == "__main__":
    archive = Path("downloads/ngspice-47_64.7z")
    NgspiceInstaller(archive).install()
