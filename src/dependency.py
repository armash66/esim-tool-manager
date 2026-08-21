from dataclasses import dataclass
from pathlib import Path
from config import load_config, get_install_dir
from registry import TOOLS, get_detector


class DependencyState:
    INSTALLED = "INSTALLED"
    NOT_INSTALLED = "NOT_INSTALLED"
    BROKEN = "BROKEN"
    UNAVAILABLE = "UNAVAILABLE"


@dataclass
class DependencyStatus:
    name: str
    state: str
    path: str | None
    version: str | None
    message: str


class DependencyChecker:
    def check_tool(self, tool_name: str) -> DependencyStatus:
        tool = TOOLS.get(tool_name.lower())
        if not tool or not tool["detector"]:
            return DependencyStatus(
                name=tool_name.capitalize(),
                state=DependencyState.UNAVAILABLE,
                path=None,
                version=None,
                message="Detection unavailable",
            )

        detector = tool["detector"]()
        info = detector.detect()

        # Check for broken installation: metadata exists but binary is missing/invalid
        metadata_path = get_install_dir() / tool_name.lower() / "metadata.json"
        if metadata_path.is_file():
            try:
                import json
                with open(metadata_path) as f:
                    meta = json.load(f)
                meta_path = meta.get("path")
                if meta_path and not Path(meta_path).is_file():
                    return DependencyStatus(
                        name=info.name,
                        state=DependencyState.BROKEN,
                        path=meta_path,
                        version=meta.get("version"),
                        message="Executable missing (broken installation)",
                    )
            except Exception:
                pass

        if info.installed:
            if info.path and not Path(info.path).is_file():
                return DependencyStatus(
                    name=info.name,
                    state=DependencyState.BROKEN,
                    path=info.path,
                    version=info.version,
                    message="Executable missing (broken installation)",
                )

            return DependencyStatus(
                name=info.name,
                state=DependencyState.INSTALLED,
                path=info.path,
                version=info.version,
                message="Executable available",
            )
        else:
            return DependencyStatus(
                name=info.name,
                state=DependencyState.NOT_INSTALLED,
                path=None,
                version=None,
                message="Not installed",
            )

    def check_environment(self) -> dict:
        cfg = load_config()
        install_dir = get_install_dir()
        dir_exists = install_dir.is_dir()

        return {
            "install_dir_path": str(install_dir),
            "install_dir_exists": dir_exists,
            "config_valid": True,
        }

    def check_all(self) -> dict:
        results = {}
        for tool_name in TOOLS.keys():
            results[tool_name] = self.check_tool(tool_name)
        env = self.check_environment()
        return {"tools": results, "environment": env}
