# eSim Tool Manager

Automated management system for external EDA tools and dependencies required by the eSim simulation workflow.

## Overview

eSim relies on several open-source EDA tools (KiCad, Ngspice, GHDL, Verilator) for schematic design, circuit simulation, and HDL processing. Manual setup often results in environment misconfigurations, PATH mismatches, broken dependencies, and unverified tool versions.

eSim Tool Manager unifies these external tools into a single management layer. It provides dynamic detection, automated installation, semantic update checking, environment health diagnostics, versioned storage, and safe rollback mechanisms accessible through both CLI and Desktop GUI.

## Features

| Feature | Implementation Details |
|---|---|
| Tool Detection | Discovers executables dynamically on system PATH and platform-standard directories |
| Installation | Handles multi-strategy installations (WinGet, release archives, package managers) |
| Version Management | Extracts precise version strings via executable CLI flags and metadata |
| Safe Upgrade | Stages upgrades as candidate builds and verifies executable integrity before activation |
| Rollback | Automatically restores prior active version if candidate verification fails |
| Updates | Compares installed versions against available releases using semantic versioning |
| Dependency Checks | Evaluates toolchain readiness state (READY vs INCOMPLETE) across all managed tools |
| Configuration | Persists install paths and system settings in `~/.esim-tools/config.json` |
| Environment / PATH | Detects PATH status and generates shell-specific export commands (PowerShell, Cmd, Bash) |
| CLI | Full sub-command interface (`list`, `check`, `doctor`, `install`, `update`, `config`, `env`) |
| Desktop GUI | Modern Tkinter interface with Activity Log, status indicators, and one-click actions |
| Logging | Audit logging to `~/.esim-tools/logs/manager.log` and standard output |
| Platform Support | Platform-adapter architecture supporting Windows and Linux environments |

Managed toolchain: **KiCad · Ngspice · GHDL · Verilator**

## Architecture

```text
                     CLI / Desktop GUI (gui.py)
                                 |
                            Tool Registry
                    _____________|_____________
                   |             |             |
              Detectors     Installers     Updaters
                   |             |             |
                   +-------------+-------------+
                                 |
                         Platform Adapter
                                 |
                          Windows / Linux
```

- **Separation of Concerns**: Detection, installation, and update logic are encapsulated into dedicated components for each tool.
- **Central Registry**: Provides a uniform interface for querying tool metadata, detectors, installers, and updaters.
- **Platform Adapter**: Decouples OS-specific path resolving and package manager invocations from application logic.
- **Verification First**: Executable discovery and version checks must succeed before an installation or upgrade is marked valid.

## Installation

```powershell
# Clone repository
git clone https://github.com/armash66/esim-tool-manager.git
cd esim-tool-manager

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install requirements
python -m pip install -r requirements.txt
```

## Usage

### CLI Commands

| Command | Description |
|---|---|
| `python src/manager.py list` | List all managed tools and brief installation status |
| `python src/manager.py check` | Display detailed tool status including version and executable path |
| `python src/manager.py doctor [--json]` | Run comprehensive health diagnostics (supports `--json` output) |
| `python src/manager.py install <tool>` | Install a specific tool (`kicad`, `ngspice`, `ghdl`, `verilator`) |
| `python src/manager.py install all [--dry-run]` | Install all missing tools while skipping healthy installations |
| `python src/manager.py update [tool]` | Check for available updates or trigger upgrade for a tool |
| `python src/manager.py snapshot` | Create a JSON snapshot manifest of the current toolchain state |
| `python src/manager.py verify --manifest <file>` | Verify environment state against a toolchain manifest |
| `python src/manager.py sync --manifest <file> [--dry-run]` | Synchronize toolchain environment to match a target manifest |
| `python src/manager.py config` | View or update configuration settings |
| `python src/manager.py env` | Inspect tool binary paths and print shell PATH export commands |
| `python src/manager.py gui` | Launch the Desktop GUI application |

### Desktop GUI

```powershell
python src/manager.py gui
```

## Managed Tools

| Tool | Category | Detection Strategy | Installation Strategy | Update Checking |
|---|---|---|---|---|
| **KiCad** | Core EDA | Executable CLI / `%LOCALAPPDATA%` & `%ProgramFiles%` discovery | WinGet (`--scope user --force`) | WinGet package query |
| **Ngspice** | Circuit Simulator | Executable CLI / metadata / PATH | Versioned 7z release archive | Local release comparison |
| **GHDL** | VHDL Simulator | Executable CLI / system PATH | WinGet / `apt` | WinGet package query |
| **Verilator** | Verilog Simulator | Executable CLI / MSYS2 `mingw64` discovery | MSYS2 `pacman` / `apt` | WinGet / `pacman -Si` query |

## Versioning and Rollback

Managed tools supporting versioned installations (e.g., Ngspice) are organized in isolated directories:

```text
~/.esim-tools/ngspice/
├── versions/
│   ├── 47/
│   └── 48/
├── active -> versions/47/
└── metadata.json
```

1. **Candidate Staging**: New release versions are extracted into an isolated directory under `versions/<version>/`.
2. **Verification**: Executable presence and version output are verified prior to activation.
3. **Atomic Swap**: Upon successful verification, the `active` pointer and metadata are updated to the candidate build.
4. **Rollback**: If candidate verification fails, the installer aborts and retains the existing active installation intact.

## Testing

Run the automated test suite with pytest:

```powershell
pytest -v
```

Current test suite: **55 passed**

Tests cover tool detection, multi-strategy installation, metadata persistence, registry wiring, dependency health states, configuration, CLI subcommands, GUI wiring, version comparison, manifest planning, dry-run safety, and safe upgrade/rollback logic.

## Documentation

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Component design, data flows, and subsystem architecture
- [TOOLCHAIN_MANIFEST.md](docs/TOOLCHAIN_MANIFEST.md) - Reproducible environment manifests, snapshotting, and dry-run guide
- [USER_GUIDE.md](docs/USER_GUIDE.md) - Detailed operating guide for CLI commands and Desktop GUI
- [REQUIREMENTS.md](docs/REQUIREMENTS.md) - Mapping of implementation against technical requirements

## Project Structure

```text
esim-tool-manager/
├── src/
│   ├── manager.py          # CLI entry point and subcommand handlers
│   ├── gui.py              # Tkinter Desktop GUI interface
│   ├── manifest.py         # Declarative manifests, planner, and OperationResult
│   ├── registry.py         # Central tool registry
│   ├── detector.py         # Tool detection logic
│   ├── installer.py        # Installation workflows
│   ├── updater.py          # Version comparison and update handlers
│   ├── dependency.py       # Dependency health checker
│   ├── config.py           # Configuration management
│   ├── platform_adapter.py # OS abstraction layer (Windows/Linux)
│   └── logger.py           # Persistent audit logging
├── tests/                  # Automated pytest test suite
├── docs/                   # System documentation
├── requirements.txt        # Python dependencies
├── README.md               # Repository overview
└── LICENSE                 # License file
```

## Platform Support

- **Windows**: Primary target environment. Verified on Windows 10/11 using WinGet, MSYS2, PowerShell, and native binary distributions.
- **Linux**: Supported via `LinuxAdapter` abstraction using system package managers (`apt`, `dnf`, `pacman`).

## License

MIT License. See [LICENSE](LICENSE) for details.
