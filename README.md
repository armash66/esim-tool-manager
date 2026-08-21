# eSim Tool Manager

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Test Status](https://img.shields.io/badge/tests-19%20passed-success)](tests/)

A lightweight, robust, and extensible Tool Manager for the **eSim** EDA workflow. It automates tool detection, multi-strategy installation, version management, health diagnostics, configuration management, and audit logging.

---

## Key Features

- 🔍 **Decoupled Tool Detection (`detector.py`)**: Detects tools via `PATH`, system installation directories (e.g. `Program Files`), or local versioned environments.
- 📦 **Multi-Strategy Installation (`installer.py`)**: Supports package managers (**WinGet** for KiCad) and direct archive extraction (**7z** for Ngspice).
- 🛡️ **Versioned Installations & Safe Rollback (`installer.py`)**: Installs archives into `versions/<ver>/`, verifies candidate executables, and performs automatic rollback if activation fails.
- 🩺 **Environment Doctor (`dependency.py`)**: Diagnostic readiness command reporting `INSTALLED`, `NOT_INSTALLED`, `BROKEN`, and `UNAVAILABLE` states.
- ⚙️ **Centralized Configuration (`config.py`)**: Manages settings in `~/.esim-tools/config.json` with fallback defaults.
- 🗃️ **Tool Registry (`registry.py`)**: Central registry mapping tool categories, detectors, installers, and updaters.
- 📜 **Audit Logging (`logger.py`)**: Automated log stream written to `~/.esim-tools/logs/manager.log`.
- 🧪 **Automated Test Suite (`tests/`)**: 19 unit & integration tests written with `pytest`.

---

## Supported Tools

| Tool | Category | Detection Mechanism | Installation Strategy |
|---|---|---|---|
| **KiCad** | `core-tool` | `PATH` + Version folder scan (`C:\Program Files\KiCad`) | WinGet (`KiCad.KiCad`) |
| **Ngspice** | `core-tool` | `PATH` + `~/.esim-tools/ngspice/` + `metadata.json` | 7z Archive Extraction + Metadata |
| **GHDL** | `core-tool` | `PATH` + `~/.esim-tools/ghdl/` | Manual / Package Manager |
| **Verilator** | `core-tool` | `PATH` + `~/.esim-tools/verilator/` | Manual / Package Manager |

---

## Quick Start

### 1. Installation & Prerequisites
Clone the repository and set up a virtual environment:
```bash
git clone https://github.com/armash66/esim-tool-manager.git
cd esim-tool-manager

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Basic Commands
```bash
# List all registered tools
python src/manager.py list

# Run detection checks
python src/manager.py check

# Run environment doctor diagnostics
python src/manager.py doctor

# Install Ngspice or KiCad
python src/manager.py install ngspice
python src/manager.py install kicad

# Check or apply updates
python src/manager.py update

# View or update configuration
python src/manager.py config
python src/manager.py config --set auto_update true
```

---

## Running Tests

Run the complete test suite:
```bash
pytest
```
All 19 tests run isolated from local machine state using temporary directories (`tmp_path`) and test mocks.

---

## Project Structure

```
esim-tool-manager/
├── README.md              # Project Overview & Quick Start
├── LICENSE                # MIT License
├── requirements.txt       # Python dependencies
├── src/                   # Source Code
│   ├── manager.py         # Application CLI entry point
│   ├── registry.py        # Central Tool Registry
│   ├── detector.py        # Tool Detectors & ToolInfo dataclass
│   ├── installer.py       # Installers & Safe Rollback logic
│   ├── updater.py         # Version Updaters
│   ├── dependency.py     # Environment Doctor & Dependency Checker
│   ├── config.py          # Configuration Manager (~/.esim-tools/config.json)
│   └── logger.py          # Audit Logging (~/.esim-tools/logs/manager.log)
├── tests/                 # Automated Test Suite (19 tests)
└── docs/                  # Detailed Documentation
    ├── ARCHITECTURE.md    # Architecture & Rollback Workflow
    ├── USER_GUIDE.md       # User Guide & Command Examples
    └── REQUIREMENTS.md   # Internship Task Requirement Mapping
```

---

## Documentation

- 📐 [Architecture Documentation](docs/ARCHITECTURE.md)
- 📖 [User Guide](docs/USER_GUIDE.md)
- 📋 [Task Requirement Mapping](docs/REQUIREMENTS.md)
