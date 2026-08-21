import argparse
from pathlib import Path

from config import load_config, save_config
from dependency import DependencyChecker, DependencyState
from detector import print_tool
from logger import get_logger
from registry import get_all_detectors, get_detector, get_installer, get_updater, list_tools, TOOLS

logger = get_logger()


import sys

def cmd_gui(args: argparse.Namespace) -> None:
    logger.info("Command executed: gui")
    from gui import launch_gui
    launch_gui()


def cmd_uninstall(args: argparse.Namespace) -> None:
    tool_name = args.tool.lower()
    logger.info(f"Command executed: uninstall {tool_name}")
    installer = get_installer(tool_name)
    if not installer or not hasattr(installer, "uninstall"):
        print(f"No uninstaller available for '{tool_name}'.")
        return

    print(f"Uninstalling {tool_name}...")
    success = installer.uninstall()
    if success:
        print(f"Successfully uninstalled {tool_name}.")
    else:
        print(f"Failed to uninstall {tool_name}.")


def cmd_env(args: argparse.Namespace) -> None:
    logger.info("Command executed: env")
    checker = DependencyChecker()
    report = checker.check_all()

    print("eSim Environment Variable Configuration\n")
    bin_paths = []
    for tool_name, status in report["tools"].items():
        if status.state == DependencyState.INSTALLED and status.path:
            parent_dir = str(Path(status.path).parent)
            bin_paths.append(parent_dir)
            status_str = "ON PATH" if status.is_on_path else "MISSING FROM PATH"
            print(f"{status.name}: {parent_dir} [{status_str}]")

    print("\nEnvironment PATH Configuration Instructions:")
    if sys.platform == "win32":
        ps_path = ";".join(bin_paths)
        print("  PowerShell:")
        print(f'    $env:Path += ";{ps_path}"')
        print("  Command Prompt:")
        print(f'    set PATH=%PATH%;{ps_path}\n')
    else:
        bash_path = ":".join(bin_paths)
        print("  POSIX Shell (Bash/Zsh):")
        print(f'    export PATH="$PATH:{bash_path}"\n')


def cmd_config(args: argparse.Namespace) -> None:
    logger.info(f"Command executed: config (set={args.set})")
    cfg = load_config()

    if args.set:
        key, val = args.set
        if key in cfg:
            if isinstance(cfg[key], bool):
                cfg[key] = val.lower() in ("true", "1", "yes")
            else:
                cfg[key] = val
            save_config(cfg)
            msg = f"Updated config: {key} = {cfg[key]}"
            print(msg)
            logger.info(msg)
        else:
            msg = f"Unknown config key '{key}'. Available keys: {', '.join(cfg.keys())}"
            print(msg)
            logger.warning(msg)
        return

    print("eSim Tool Manager Configuration\n")
    print(f"Install directory: {cfg.get('install_directory')}")
    print(f"Auto update:       {cfg.get('auto_update')}\n")


def cmd_update(args: argparse.Namespace) -> None:
    logger.info(f"Command executed: update (tool={args.tool})")
    if args.tool:
        tool_name = args.tool.lower()
        updater = get_updater(tool_name)
        if not updater:
            msg = f"Update for tool '{args.tool}' is not supported."
            print(msg)
            logger.warning(msg)
            return
        updater.update()
    else:
        print("eSim Tool Updates Check\n")
        for tool_name, info in TOOLS.items():
            updater = get_updater(tool_name)
            if not updater:
                continue
            status = updater.check_update()
            if not status["installed"]:
                print(f"{info['name']}\n  [-] Not installed\n")
                continue

            print(f"{info['name']}")
            print(f"  Installed: {status['installed_version']}")
            print(f"  Available: {status['latest_version']}")
            if status["needs_update"]:
                print(f"  [!] Update available: {status['installed_version']} -> {status['latest_version']}")
            else:
                print("  [+] Up to date")
            print()


def format_tool_check(info) -> None:
    print(f"\n{info.name}")
    if info.installed:
        print("  [+] Installed")
        ver_str = info.version if info.version is not None else "(unavailable)"
        print(f"  [+] Version: {ver_str}")
    else:
        print("  [-] Not installed")


def check_all() -> None:
    for detector in get_all_detectors():
        print_tool(detector.detect())
        print()


def check_all_detailed() -> None:
    print("eSim Tool Manager Status Check")
    for detector in get_all_detectors():
        format_tool_check(detector.detect())
    print()


def cmd_list(args: argparse.Namespace) -> None:
    logger.info("Command executed: list")
    check_all()


def cmd_check(args: argparse.Namespace) -> None:
    logger.info("Command executed: check")
    check_all_detailed()


def cmd_doctor(args: argparse.Namespace) -> None:
    logger.info("Command executed: doctor")
    checker = DependencyChecker()
    report = checker.check_all()

    if getattr(args, "json", False):
        import json
        json_out = {
            "tools": {},
            "environment": report["environment"],
            "status": "READY" if not any(
                st.state in (DependencyState.NOT_INSTALLED, DependencyState.BROKEN)
                for st in report["tools"].values()
            ) else "INCOMPLETE"
        }
        for tool_name, status in report["tools"].items():
            json_out["tools"][tool_name] = {
                "installed": status.state == DependencyState.INSTALLED,
                "version": status.version,
                "path": status.path,
                "on_path": status.is_on_path,
                "state": str(status.state),
                "message": status.message
            }
        print(json.dumps(json_out, indent=2))
        return

    print("eSim Environment Doctor\n")
    print("Core Managed Tools")
    core_missing = []
    for tool_name, status in report["tools"].items():
        print(f"\n{status.name}")
        if status.state == DependencyState.INSTALLED:
            print("  [+] Installed")
            ver_str = status.version if status.version is not None else "(unavailable)"
            print(f"  [+] Version: {ver_str}")
            print(f"  [+] {status.message}")
            path_msg = "Path in system PATH" if status.is_on_path else "Path NOT in system PATH (run 'env' for instructions)"
            print(f"  {'[+]' if status.is_on_path else '[!]'} {path_msg}")
            logger.info(f"Doctor check: {status.name} INSTALLED ({ver_str}), on_path={status.is_on_path}")
        elif status.state == DependencyState.BROKEN:
            print("  [!] Broken Installation")
            print(f"  [!] {status.message}")
            core_missing.append(status.name)
            logger.warning(f"Doctor check: {status.name} BROKEN")
        elif status.state == DependencyState.NOT_INSTALLED:
            print("  [-] Not installed")
            core_missing.append(status.name)
            logger.info(f"Doctor check: {status.name} NOT INSTALLED")

    print("\nConfiguration")
    env = report["environment"]
    if env["install_dir_exists"]:
        print(f"  [+] Install directory exists ({env['install_dir_path']})")
    else:
        print(f"  [-] Install directory missing ({env['install_dir_path']})")

    if env["config_valid"]:
        print("  [+] Configuration valid")

    print("\n" + "=" * 45)
    if core_missing:
        missing_str = ", ".join(core_missing)
        msg = f"Toolchain Status: INCOMPLETE (missing/broken: {missing_str})"
        print(msg)
        logger.warning(msg)
    else:
        msg = "Toolchain Status: READY"
        print(msg)
        logger.info(msg)
    print("=" * 45 + "\n")


def cmd_install(args: argparse.Namespace) -> None:
    logger.info(f"Command executed: install (tool={args.tool}, dry_run={args.dry_run})")
    tool_name = args.tool.lower()

    if tool_name == "all":
        if args.dry_run:
            from manifest import ToolchainManager
            tm = ToolchainManager()
            # Generate a temporary plan equivalent to dry-run sync with current missing tools
            manifest_data = {"schema_version": 1, "tools": {}}
            for t_name in TOOLS.keys():
                manifest_data["tools"][t_name] = {"version": "latest"}
            plans = tm.planner.plan(manifest_data)
            print("Toolchain Plan (Dry-Run)\n")
            for p in plans:
                print(f"  {p.tool:<12} {p.action:<12} {p.message}")
            print("\nNo changes made.")
            return

        print("Installing all missing tools...\n")
        skipped = []
        succeeded = []
        failed = []
        for t_name, t_info in TOOLS.items():
            installer = get_installer(t_name)
            detector = get_detector(t_name)
            if not installer or not detector:
                continue

            det_info = detector.detect()
            if det_info.installed:
                print(f"{t_info['name']}: already installed, skipping.")
                skipped.append(t_info['name'])
                continue

            print(f"{t_info['name']}: installing...")
            try:
                success = installer.install()
                if success:
                    print(f"{t_info['name']}: installation completed successfully.")
                    succeeded.append(t_info['name'])
                else:
                    print(f"{t_info['name']}: installation failed.")
                    failed.append(t_info['name'])
            except Exception as e:
                print(f"{t_info['name']}: installation error: {e}")
                failed.append(t_info['name'])

        print()
        if failed:
            print(f"Install All completed with {len(failed)} failure(s): {', '.join(failed)}")
            logger.error(f"Install All failures: {', '.join(failed)}")
        else:
            print("All installation tasks completed.")
        if skipped:
            print(f"Skipped (already installed): {', '.join(skipped)}")
        if succeeded:
            print(f"Newly installed: {', '.join(succeeded)}")
        return

    if args.dry_run:
        print(f"[DRY-RUN] Would install {args.tool}. No changes made.")
        return

    installer = get_installer(tool_name)
    detector = get_detector(tool_name)

    if not installer or not detector:
        supported = ", ".join(list_tools())
        msg = f"Tool '{args.tool}' is not supported. Supported tools: {supported}"
        print(msg)
        logger.warning(msg)
        return

    print(f"Installing {args.tool}...\n")
    success = installer.install()

    if not success:
        print("\nInstallation failed.")
        logger.error(f"Installation of {args.tool} failed.")
        return

    print("\nVerifying installation...\n")
    info = detector.detect()
    print_tool(info)
    logger.info(f"Installation of {args.tool} completed and verified.")


def cmd_snapshot(args: argparse.Namespace) -> None:
    logger.info("Command executed: snapshot")
    from manifest import ToolchainManager
    tm = ToolchainManager()
    out_path = Path(args.output)
    print("Creating toolchain snapshot...\n")
    manifest = tm.snapshot(out_path)
    for tool_name, data in manifest["tools"].items():
        st = f"{data['version']}" if data["installed"] else "MISSING"
        print(f"  {tool_name:<12} {st}")
    print(f"\nToolchain snapshot written to {out_path}")


def cmd_verify(args: argparse.Namespace) -> None:
    logger.info(f"Command executed: verify (manifest={args.manifest})")
    from manifest import ToolchainManager
    tm = ToolchainManager()
    m_path = Path(args.manifest)
    print("Toolchain Verification\n")
    try:
        results = tm.verify_manifest(m_path)
        all_ok = True
        for r in results:
            status_str = "OK" if r.success else "MISMATCH / MISSING"
            if not r.success:
                all_ok = False
            print(f"  {r.tool:<12} required: {r.new_version or 'N/A':<10} installed: {r.old_version or 'MISSING':<10} {status_str}")
        print("\n" + "=" * 45)
        print(f"Result: {'MATCH' if all_ok else 'INCOMPLETE'}")
        print("=" * 45 + "\n")
    except Exception as e:
        print(f"Verification error: {e}")
        logger.error(f"Verification error: {e}")


def cmd_sync(args: argparse.Namespace) -> None:
    logger.info(f"Command executed: sync (manifest={args.manifest}, dry_run={args.dry_run})")
    from manifest import ToolchainManager
    tm = ToolchainManager()
    m_path = Path(args.manifest)
    print("Reading toolchain manifest...\n")
    try:
        results = tm.sync_manifest(m_path, dry_run=args.dry_run)
        all_ok = True
        for r in results:
            if not r.success and r.action != "skip":
                all_ok = False
            print(f"  {r.tool:<12} action: {r.action:<10} result: {'SUCCESS' if r.success else 'FAILED'} ({r.message})")

        print("\n" + "=" * 45)
        if args.dry_run:
            print("Toolchain sync dry-run complete. No changes made.")
        else:
            print(f"Toolchain Sync Result: {'SUCCESS' if all_ok else 'INCOMPLETE'}")
        print("=" * 45 + "\n")
    except Exception as e:
        print(f"Sync error: {e}")
        logger.error(f"Sync error: {e}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="esim-manager",
        description="Manage EDA tools for the eSim workflow.",
    )
    subparsers = parser.add_subparsers(dest="command")

    list_parser = subparsers.add_parser("list", help="List all tools and their status.")
    list_parser.set_defaults(func=cmd_list)

    check_parser = subparsers.add_parser("check", help="Perform detection checks and report tool status.")
    check_parser.set_defaults(func=cmd_check)

    doctor_parser = subparsers.add_parser("doctor", help="Run environment diagnostics.")
    doctor_parser.add_argument("--json", action="store_true", help="Output diagnostics in JSON format")
    doctor_parser.set_defaults(func=cmd_doctor)

    gui_parser = subparsers.add_parser("gui", help="Launch Tkinter desktop GUI.")
    gui_parser.set_defaults(func=cmd_gui)

    env_parser = subparsers.add_parser("env", help="Show environment variable and PATH configuration.")
    env_parser.set_defaults(func=cmd_env)

    config_parser = subparsers.add_parser("config", help="View or modify configuration.")
    config_parser.add_argument("--set", nargs=2, metavar=("KEY", "VALUE"), help="Set a configuration key and value")
    config_parser.set_defaults(func=cmd_config)

    update_parser = subparsers.add_parser("update", help="Check for or install updates.")
    update_parser.add_argument("tool", nargs="?", help="Optional tool name to update")
    update_parser.set_defaults(func=cmd_update)

    install_parser = subparsers.add_parser("install", help="Install a managed tool (or 'all' for all missing tools).")
    install_parser.add_argument("tool", help="Name of the tool to install, or 'all' to install all missing tools")
    install_parser.add_argument("--dry-run", action="store_true", help="Simulate installation without making changes")
    install_parser.set_defaults(func=cmd_install)

    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall a managed tool.")
    uninstall_parser.add_argument("tool", help="Name of the tool to uninstall")
    uninstall_parser.set_defaults(func=cmd_uninstall)

    snapshot_parser = subparsers.add_parser("snapshot", help="Create a JSON snapshot manifest of current toolchain state.")
    snapshot_parser.add_argument("--output", "-o", default="esim-toolchain.json", help="Output path for snapshot JSON file")
    snapshot_parser.set_defaults(func=cmd_snapshot)

    verify_parser = subparsers.add_parser("verify", help="Verify environment state against a toolchain manifest.")
    verify_parser.add_argument("--manifest", "-m", default="esim-toolchain.json", help="Path to manifest JSON file")
    verify_parser.set_defaults(func=cmd_verify)

    sync_parser = subparsers.add_parser("sync", help="Synchronize toolchain environment to match a manifest.")
    sync_parser.add_argument("--manifest", "-m", default="esim-toolchain.json", help="Path to manifest JSON file")
    sync_parser.add_argument("--dry-run", action="store_true", help="Simulate sync operations without executing them")
    sync_parser.set_defaults(func=cmd_sync)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
