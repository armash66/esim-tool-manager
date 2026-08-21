import argparse

from config import load_config, save_config
from dependency import DependencyChecker, DependencyState
from detector import print_tool
from logger import get_logger
from registry import get_all_detectors, get_detector, get_installer, get_updater, list_tools, TOOLS

logger = get_logger()


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
    print("eSim Environment Doctor\n")
    checker = DependencyChecker()
    report = checker.check_all()

    print("Core Tools")
    missing_tools = []
    for tool_name, status in report["tools"].items():
        print(f"\n{status.name}")
        if status.state == DependencyState.INSTALLED:
            print("  [+] Installed")
            ver_str = status.version if status.version is not None else "(unavailable)"
            print(f"  [+] Version: {ver_str}")
            print(f"  [+] {status.message}")
            logger.info(f"Doctor check: {status.name} INSTALLED ({ver_str})")
        elif status.state == DependencyState.BROKEN:
            print("  [!] Broken Installation")
            print(f"  [!] {status.message}")
            missing_tools.append(status.name)
            logger.warning(f"Doctor check: {status.name} BROKEN")
        elif status.state == DependencyState.NOT_INSTALLED:
            print("  [-] Not installed")
            missing_tools.append(status.name)
            logger.info(f"Doctor check: {status.name} NOT INSTALLED")
        elif status.state == DependencyState.UNAVAILABLE:
            print("  [o] Detection unavailable")

    print("\nConfiguration")
    env = report["environment"]
    if env["install_dir_exists"]:
        print(f"  [+] Install directory exists ({env['install_dir_path']})")
    else:
        print(f"  [-] Install directory missing ({env['install_dir_path']})")

    if env["config_valid"]:
        print("  [+] Configuration valid")

    print("\n" + "=" * 45)
    if missing_tools:
        missing_str = ", ".join(missing_tools)
        msg = f"Overall Status: NOT READY (missing/broken: {missing_str})"
        print(msg)
        logger.warning(msg)
    else:
        msg = "Overall Status: READY"
        print(msg)
        logger.info(msg)
    print("=" * 45 + "\n")


def cmd_install(args: argparse.Namespace) -> None:
    logger.info(f"Command executed: install (tool={args.tool})")
    tool_name = args.tool.lower()
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
    doctor_parser.set_defaults(func=cmd_doctor)

    config_parser = subparsers.add_parser("config", help="View or modify configuration.")
    config_parser.add_argument("--set", nargs=2, metavar=("KEY", "VALUE"), help="Set a configuration key and value")
    config_parser.set_defaults(func=cmd_config)

    update_parser = subparsers.add_parser("update", help="Check for or install updates.")
    update_parser.add_argument("tool", nargs="?", help="Optional tool name to update")
    update_parser.set_defaults(func=cmd_update)

    install_parser = subparsers.add_parser("install", help="Install a tool.")
    install_parser.add_argument("tool", help="Name of the tool to install (e.g. kicad, ngspice)")
    install_parser.set_defaults(func=cmd_install)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
