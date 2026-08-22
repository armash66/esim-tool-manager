# eSim Tool Manager

Automated toolchain management system for external EDA tools and dependencies required by eSim.

## What It Does

eSim Tool Manager prepares and maintains the external toolchain used by eSim.

It can:
- Install and uninstall supported tools
- Detect installed versions and executable paths
- Check for updates against upstream sources
- Diagnose missing tools and platform prerequisites
- Create and verify reproducible toolchain manifests
- Synchronize an environment with a manifest
- Provide both CLI and Tkinter Desktop GUI interfaces

## Managed Tools

| Tool | Purpose | Detection Strategy | Installation Strategy |
|---|---|---|---|
| **KiCad** | Schematic and PCB design | Executable CLI / `%LOCALAPPDATA%` & `%ProgramFiles%` | WinGet (`--scope user --force`) |
| **Ngspice** | Circuit simulation | Executable CLI / metadata / PATH | Versioned 7z release archive |
| **GHDL** | VHDL simulation | Executable CLI / WinGet packages / system PATH | WinGet / `apt` |
| **Verilator** | Verilog/SystemVerilog simulation | Executable CLI / MSYS2 `mingw64` discovery | MSYS2 `pacman` / `apt` |

## Prerequisites

The manager checks platform prerequisites before performing installations:

- **Windows**: WinGet is used for KiCad and GHDL. MSYS2 (`pacman`) is required for Verilator.
- **Linux**: Standard package managers (`apt`) are used where supported.

If a required prerequisite is missing, the manager halts installation cleanly, reports the problem, and provides actionable recommendations (e.g., download instructions) rather than failing silently.

## Verification

Installation success is not based solely on package manager return codes.

After installation, the manager verifies the actual tool executable and version using its detector. This catches cases where a package manager reports a successful installation but the expected binary remains unavailable on disk.

## Quick Start

```powershell
# Clone & setup virtual environment
git clone https://github.com/armash66/esim-tool-manager.git
cd esim-tool-manager
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
python -m pip install -r requirements.txt

# Run health diagnostics
python src\manager.py doctor

# Launch Desktop GUI
python src\manager.py gui
```

### Common CLI Tasks

```powershell
# Install all missing tools
python src\manager.py install all

# Inspect status and PATH environment
python src\manager.py check
python src\manager.py env
```

## Features

| Feature | CLI | GUI |
|---|:---:|:---:|
| Tool detection | ✓ | ✓ |
| Installation | ✓ | ✓ |
| Uninstallation | ✓ | ✓ |
| Updates | ✓ | ✓ |
| Diagnostics | ✓ | ✓ |
| Prerequisite checks | ✓ | ✓ |
| Toolchain manifest | ✓ | — |
| Dry run | ✓ | — |
| Synchronization | ✓ | — |

## Testing

The project includes an automated pytest suite covering installers, detectors, updaters, diagnostics, GUI behavior, manifests, planning, verification, and failure handling.

Current test status: **56 tests passing**.

```powershell
pytest -q
```

## Documentation

- [USER_GUIDE.md](docs/USER_GUIDE.md) - Operating guide for CLI commands and Desktop GUI
- [DESIGN.md](docs/DESIGN.md) - Functional specifications, architecture, and technical design

## License

MIT License. See [LICENSE](LICENSE) for details.
