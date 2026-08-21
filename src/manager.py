import argparse

from detector import KiCadDetector, NgspiceDetector, print_tool

DETECTORS = [
    KiCadDetector(),
    NgspiceDetector(),
]


def check_all() -> None:
    for detector in DETECTORS:
        print_tool(detector.detect())
        print()


def cmd_list(args: argparse.Namespace) -> None:
    check_all()


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="esim-manager",
        description="Manage EDA tools for the eSim workflow.",
    )
    subparsers = parser.add_subparsers(dest="command")

    list_parser = subparsers.add_parser("list", help="List all tools and their status.")
    list_parser.set_defaults(func=cmd_list)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
