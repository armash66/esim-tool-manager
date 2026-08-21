# eSim Tool Manager

A command-line tool for managing external tools and dependencies used by eSim.

## Overview

eSim integrates multiple external tools for schematic design, simulation, HDL processing, and related workflows. Managing these tools manually can involve installation, version verification, configuration, environment setup, and recovery from failed upgrades.

eSim Tool Manager provides a centralized CLI for detecting, installing, verifying, updating, configuring, and diagnosing managed tools.

The current implementation targets Windows and uses platform-specific installation strategies where required.

## Features

- Tool detection with executable and version discovery
- Tool installation through multiple installation strategies
- Centralized tool registry
- Versioned installations
- Candidate verification before activation
- Automatic rollback on failed upgrades
- Installed/available version comparison
- Configuration management
- Environment and PATH diagnostics
- Dependency and installation health checks
- Persistent audit logging
- Dual Interfaces: Command Line Interface (CLI) and Desktop Graphical User Interface (GUI)
- Cross-Platform Adapters (Windows & Linux abstraction)
- Automated unit and integration tests (22 tests)

## Supported Tools

| Tool | Detection | Installation | Updates |
|------|-----------|--------------|---------|
| KiCad | Yes | WinGet | Yes |
| Ngspice | Yes | 7z archive | Yes |
| GHDL | Yes | WinGet / apt | Yes |
| Verilator | Yes | WinGet / apt | Yes |

## Architecture

```text
                         CLI / Desktop GUI (gui.py)
                                    |
                                 Manager
                                    |
                               Tool Registry
                   _________________|_________________
                  |                 |                 |
             Detectors         Installers        Updaters
                  |                 |                 |
                  +-----------------+-----------------+
                                    |
                           Dependency Checker
                                    |
                +-------------------+-------------------+
                |                   |                   |
          Configuration          Logger          Platform Adapter
                                              (Windows / Linux)
```

The registry provides a common lookup layer for tool-specific detectors, installers, and updaters. Tool implementations remain responsible for platform-specific behavior.

### Installation strategies

KiCad is installed through Windows Package Manager:

```text
Manager -> KiCad Installer -> WinGet -> KiCad -> Detector
```

Ngspice is installed from a release archive:

```text
Manager -> Ngspice Installer -> Archive Extraction
       -> Candidate Verification -> Activation
```

### Versioned installation and rollback

Managed Ngspice installations use versioned directories:

```text
~/.esim-tools/ngspice/
├── versions/
│   ├── <version>/
│   └── ...
├── active/
└── metadata.json
```

Updates are staged as candidates and verified before activation. If verification fails, the previous active installation is restored automatically.

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for the complete design.

## Installation

Clone the repository:

```bash
git clone https://github.com/armash66/esim-tool-manager.git
cd esim-tool-manager
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

The manager is operated through the command line.

### Launch Desktop GUI
```bash
python src\manager.py gui
```
Or directly run `python src\gui.py`.

### List managed tools
```bash
python src\manager.py list
```

### Check installed tools
```bash
python src\manager.py check
```

### Diagnose the eSim environment
```bash
python src\manager.py doctor
```

The diagnostic command checks tool availability, installation state, versions, managed directories, and PATH configuration.

### Install a tool
```bash
python src\manager.py install ngspice
python src\manager.py install kicad
```

### Check for updates
```bash
python src\manager.py update
```

Update a specific tool:

```bash
python src\manager.py update ngspice
```

### Manage configuration
```bash
python src\manager.py config
```

Set a configuration value:

```bash
python src\manager.py config --set auto_update true
```

Configuration is stored at: `~/.esim-tools/config.json`

### Environment configuration
```bash
python src\manager.py env
```

This reports the environment configuration required by the managed tools and can generate shell-specific PATH configuration.

## Runtime Data

The manager stores user-specific state outside the repository:

```text
~/.esim-tools/
├── config.json
├── logs/
│   └── manager.log
└── ngspice/
    ├── versions/
    ├── active/
    └── metadata.json
```

This keeps installation state, configuration, and logs separate from the application source code.

## Testing

The project uses pytest for automated testing.

Run the complete test suite:

```bash
pytest
```

Current test suite: **45 passed**

Tests cover:
- Tool detection
- Installation behavior
- Metadata handling
- Registry operations
- Dependency states
- Configuration handling
- CLI commands
- Upgrade and rollback behavior

Tests are isolated from the developer's installed toolchain and do not require the actual KiCad or Ngspice installations to execute.

## Project Structure

```text
esim-tool-manager/
├── src/
│   ├── manager.py
│   ├── registry.py
│   ├── detector.py
│   ├── installer.py
│   ├── updater.py
│   ├── dependency.py
│   ├── config.py
│   └── logger.py
├── tests/
│   ├── test_cli.py
│   ├── test_config.py
│   ├── test_dependency.py
│   ├── test_detector.py
│   ├── test_installer.py
│   ├── test_registry.py
│   └── test_rollback.py
├── docs/
│   ├── ARCHITECTURE.md
│   ├── USER_GUIDE.md
│   └── REQUIREMENTS.md
├── README.md
├── LICENSE
├── requirements.txt
└── .gitignore
```

## Design Principles

### Separation of responsibilities
Detection, installation, updating, configuration, dependency checking, and logging are implemented as separate components.

### Verification before activation
An installation is not considered valid merely because extraction or package installation completed. The resulting executable is detected and verified before being activated.

### Tool-specific installation strategies
The manager does not assume that every dependency is installed the same way. Installers encapsulate the mechanism required by each tool.

### No machine-specific paths
User and installation paths are resolved at runtime. The source code does not depend on developer-specific absolute paths.

## Requirements Coverage

| Task 5 requirement | Implementation |
|---|---|
| Tool installation | KiCad/WinGet, Ngspice/archive |
| Version management | Detection, metadata, versioned installations |
| Updates | Version comparison and update command |
| Configuration | config.json and CLI configuration |
| Path management | Environment diagnostics and shell configuration |
| Dependency checking | DependencyChecker and doctor |
| User interface | CLI |
| Installed/version information | list and check |
| Action logging | Persistent audit log |
| Package manager integration | WinGet |
| Safe upgrade | Candidate installation and verification |
| Rollback | Automatic restoration of previous version |
| Automated testing | 19 pytest tests |

See [REQUIREMENTS.md](docs/REQUIREMENTS.md) for the detailed mapping.

## Documentation

- [ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [USER_GUIDE.md](docs/USER_GUIDE.md)
- [REQUIREMENTS.md](docs/REQUIREMENTS.md)

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
