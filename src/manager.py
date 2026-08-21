import argparse

from detector import KiCadDetector, NgspiceDetector, print_tool

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

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
