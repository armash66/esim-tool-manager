import argparse

from detector import print_tool
from registry import get_all_detectors, get_detector, get_installer, get_updater, list_tools, TOOLS


def cmd_update(args: argparse.Namespace) -> None:
    if args.tool:
        tool_name = args.tool.lower()
        updater = get_updater(tool_name)
        if not updater:
            print(f"Update for tool '{args.tool}' is not supported.")
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
    check_all()


def cmd_check(args: argparse.Namespace) -> None:
    check_all_detailed()


def cmd_doctor(args: argparse.Namespace) -> None:
    print("eSim Environment Doctor\n")
    detectors = get_all_detectors()
    missing_tools = []
    
    for detector in detectors:
        info = detector.detect()
        format_tool_check(info)
        if not info.installed:
            missing_tools.append(info.name)

    print("\n" + "=" * 40)
    if missing_tools:
        missing_str = ", ".join(missing_tools)
        print(f"Overall Status: ATTENTION REQUIRED (missing tools: {missing_str})")
    else:
        print("Overall Status: READY")
    print("=" * 40 + "\n")


def cmd_install(args: argparse.Namespace) -> None:
    tool_name = args.tool.lower()
    installer = get_installer(tool_name)
    detector = get_detector(tool_name)

    if not installer or not detector:
        supported = ", ".join(list_tools())
        print(f"Tool '{args.tool}' is not supported. Supported tools: {supported}")
        return

    print(f"Installing {args.tool}...\n")
    success = installer.install()

    if not success:
        print("\nInstallation failed.")
        return

    print("\nVerifying installation...\n")
    info = detector.detect()
    print_tool(info)


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
