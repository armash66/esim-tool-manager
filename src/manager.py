from detector import KiCadDetector, NgspiceDetector, print_tool

DETECTORS = [
    KiCadDetector(),
    NgspiceDetector(),
]


def check_all() -> None:
    for detector in DETECTORS:
        print_tool(detector.detect())
        print()


if __name__ == "__main__":
    check_all()
