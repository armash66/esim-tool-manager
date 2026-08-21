import argparse
from pathlib import Path

from detector import KiCadDetector, NgspiceDetector, print_tool
from installer import KiCadInstaller, NgspiceInstaller

DETECTORS = [
    KiCadDetector(),
    NgspiceDetector(),
]


def format_tool_check(info) -> None:
    print(f"\n{info.name}")
    if info.installed:
        print("  [+] Installed")
        ver_str = info.version if info.version is not None else "(unavailable)"
        print(f"  [+] Version: {ver_str}")
    else:
        print("  [-] Not installed")


def check_all() -> None:
    for detector in DETECTORS:
        print_tool(detector.detect())
        print()


def check_all_detailed() -> None:
    print("eSim Tool Manager Status Check")
    for detector in DETECTORS:
        format_tool_check(detector.detect())
    print()


def cmd_list(args: argparse.Namespace) -> None:
    check_all()


def cmd_check(args: argparse.Namespace) -> None:
    check_all_detailed()


def cmd_install(args: argparse.Namespace) -> None:
    tool_name = args.tool.lower()

    if tool_name == "kicad":
        installer = KiCadInstaller()
        detector = KiCadDetector()
    elif tool_name == "ngspice":
        archive_path = Path("downloads/ngspice-47_64.7z")
        installer = NgspiceInstaller(archive_path)
        detector = NgspiceDetector()
    else:
        print(f"Tool '{args.tool}' is not currently supported for installation.")
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

    install_parser = subparsers.add_parser("install", help="Install a tool.")
    install_parser.add_argument("tool", help="Name of the tool to install (e.g. ngspice)")
    install_parser.set_defaults(func=cmd_install)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
