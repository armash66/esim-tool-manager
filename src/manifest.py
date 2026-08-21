import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Any, List, Optional
from packaging.version import Version, InvalidVersion

from registry import TOOLS, get_detector, get_installer, get_updater
from logger import get_logger

logger = get_logger()


@dataclass
class OperationResult:
    tool: str
    action: str  # install, uninstall, update, verify, skip
    success: bool
    old_version: Optional[str] = None
    new_version: Optional[str] = None
    message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


@dataclass
class PlannedAction:
    tool: str
    action: str  # NO_ACTION, INSTALL, UPDATE, MISMATCH, UNAVAILABLE
    current_version: Optional[str]
    required_version: Optional[str]
    message: str


class ToolchainPlanner:
    def plan(self, manifest_data: Dict[str, Any]) -> List[PlannedAction]:
        actions = []
        tools_req = manifest_data.get("tools", {})

        for tool_key in TOOLS.keys():
            detector = get_detector(tool_key)
            if not detector:
                continue

            det_info = detector.detect()
            req_info = tools_req.get(tool_key, {})
            req_ver = req_info.get("version") if isinstance(req_info, dict) else None

            if not det_info.installed:
                if req_ver:
                    action = PlannedAction(
                        tool=tool_key,
                        action="INSTALL",
                        current_version=None,
                        required_version=req_ver,
                        message=f"Missing (required: {req_ver})"
                    )
                else:
                    action = PlannedAction(
                        tool=tool_key,
                        action="NO_ACTION",
                        current_version=None,
                        required_version=None,
                        message="Not installed and not required"
                    )
            else:
                curr_ver = det_info.version
                if not req_ver:
                    action = PlannedAction(
                        tool=tool_key,
                        action="NO_ACTION",
                        current_version=curr_ver,
                        required_version=None,
                        message="Installed (unlocked)"
                    )
                elif curr_ver == req_ver:
                    action = PlannedAction(
                        tool=tool_key,
                        action="NO_ACTION",
                        current_version=curr_ver,
                        required_version=req_ver,
                        message="Installed version matches manifest"
                    )
                else:
                    try:
                        is_older = Version(curr_ver) < Version(req_ver) if (curr_ver and req_ver) else False
                    except InvalidVersion:
                        is_older = False

                    if is_older:
                        action = PlannedAction(
                            tool=tool_key,
                            action="UPDATE",
                            current_version=curr_ver,
                            required_version=req_ver,
                            message=f"Upgrade available: {curr_ver} -> {req_ver}"
                        )
                    else:
                        action = PlannedAction(
                            tool=tool_key,
                            action="MISMATCH",
                            current_version=curr_ver,
                            required_version=req_ver,
                            message=f"Version mismatch: installed {curr_ver} != required {req_ver}"
                        )
            actions.append(action)
        return actions


class ToolchainManager:
    def __init__(self):
        self.planner = ToolchainPlanner()

    def snapshot(self, output_path: Path) -> Dict[str, Any]:
        manifest = {
            "schema_version": 1,
            "tools": {}
        }
        for tool_key, info in TOOLS.items():
            detector = get_detector(tool_key)
            if detector:
                det_info = detector.detect()
                manifest["tools"][tool_key] = {
                    "installed": det_info.installed,
                    "version": det_info.version if det_info.installed else None,
                    "path": det_info.path if det_info.installed else None
                }

        output_path.write_text(json.dumps(manifest, indent=2))
        logger.info(f"Toolchain snapshot written to {output_path}")
        return manifest

    def verify_manifest(self, manifest_path: Path) -> List[OperationResult]:
        if not manifest_path.is_file():
            raise FileNotFoundError(f"Manifest file not found: {manifest_path}")

        data = json.loads(manifest_path.read_text())
        plans = self.planner.plan(data)
        results = []

        for p in plans:
            success = (p.action == "NO_ACTION")
            res = OperationResult(
                tool=p.tool,
                action="verify",
                success=success,
                old_version=p.current_version,
                new_version=p.required_version,
                message=p.message
            )
            results.append(res)
        return results

    def sync_manifest(self, manifest_path: Path, dry_run: bool = False) -> List[OperationResult]:
        if not manifest_path.is_file():
            raise FileNotFoundError(f"Manifest file not found: {manifest_path}")

        data = json.loads(manifest_path.read_text())
        plans = self.planner.plan(data)
        results = []

        for p in plans:
            if p.action == "NO_ACTION":
                results.append(OperationResult(
                    tool=p.tool,
                    action="skip",
                    success=True,
                    old_version=p.current_version,
                    new_version=p.current_version,
                    message=p.message
                ))
            elif p.action == "INSTALL":
                if dry_run:
                    results.append(OperationResult(
                        tool=p.tool,
                        action="install",
                        success=True,
                        old_version=None,
                        new_version=p.required_version,
                        message=f"[DRY-RUN] Would install {p.tool} (target version {p.required_version})"
                    ))
                else:
                    installer = get_installer(p.tool)
                    if not installer:
                        results.append(OperationResult(
                            tool=p.tool, action="install", success=False, message="No installer available"
                        ))
                    else:
                        ok = installer.install()
                        det = get_detector(p.tool)
                        info = det.detect() if det else None
                        ver = info.version if (info and info.installed) else None
                        results.append(OperationResult(
                            tool=p.tool,
                            action="install",
                            success=ok and (info.installed if info else False),
                            old_version=None,
                            new_version=ver,
                            message="Installation verified" if ok else "Installation failed"
                        ))
            elif p.action == "UPDATE":
                if dry_run:
                    results.append(OperationResult(
                        tool=p.tool,
                        action="update",
                        success=True,
                        old_version=p.current_version,
                        new_version=p.required_version,
                        message=f"[DRY-RUN] Would upgrade {p.tool} from {p.current_version} to {p.required_version}"
                    ))
                else:
                    updater = get_updater(p.tool)
                    if not updater:
                        results.append(OperationResult(
                            tool=p.tool, action="update", success=False, message="No updater available"
                        ))
                    else:
                        ok = updater.update()
                        det = get_detector(p.tool)
                        info = det.detect() if det else None
                        ver = info.version if (info and info.installed) else None
                        results.append(OperationResult(
                            tool=p.tool,
                            action="update",
                            success=ok,
                            old_version=p.current_version,
                            new_version=ver,
                            message="Update verified" if ok else "Update failed"
                        ))
            elif p.action in ("MISMATCH", "UNAVAILABLE"):
                results.append(OperationResult(
                    tool=p.tool,
                    action="sync",
                    success=False,
                    old_version=p.current_version,
                    new_version=p.required_version,
                    message=f"Cannot sync version: {p.message}"
                ))

        return results
