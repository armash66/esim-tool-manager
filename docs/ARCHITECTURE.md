# eSim Tool Manager Architecture

This document describes the architectural design, component separation, data flow, and safety mechanisms of `esim-tool-manager`.

## System Overview

```text
                         eSim Tool Manager
                                |
                 +--------------+--------------+
                 |                             |
                CLI                           GUI
                 |                             |
                 +--------------+--------------+
                                |
                         Tool Registry
                                |
              +-----------------+-----------------+
              |                 |                 |
           Detector         Installer          Updater
              |                 |                 |
              +-----------------+-----------------+
                                |
                       Platform Adapter
                                |
                         Windows / Linux
                                |
                        Toolchain Manifest
                                |
                  +-------------+-------------+
                  |             |             |
               Snapshot       Verify        Sync
                                |
                             Planner
                                |
                         OperationResult
                                |
                   +------------+------------+
                   |            |             |
                  CLI          GUI         Logger
```

## Core Architectural Design Decisions

### 1. Data Contracts (`ToolInfo`, `OperationResult`, `DependencyStatus`)
Instead of parsing raw CLI string outputs, components interact through strongly-typed data contracts:
- `ToolInfo`: (`name`, `installed`, `path`, `version`) returned by detectors.
- `OperationResult`: (`tool`, `action`, `success`, `old_version`, `new_version`, `message`) returned by installer/updater/sync operations for unified logging, CLI printing, and GUI rendering.
- `DependencyStatus`: (`INSTALLED`, `NOT_INSTALLED`, `BROKEN`, `UNAVAILABLE`) calculated by `DependencyChecker`.

### 2. Toolchain Manifest & Planning Engine (`manifest.py`)
The environment state can be modeled declaratively as a lightweight JSON manifest (`esim-toolchain.json`):
- **Desired vs Actual State**: `ToolchainPlanner` compares desired manifest versions against actual detector results.
- **Planned Actions**: Emits `NO_ACTION`, `INSTALL`, `UPDATE`, `MISMATCH`, or `UNAVAILABLE` actions.
- **Dry-Run Staging**: Preview toolchain modifications (`--dry-run`) without triggering filesystem or package manager changes.

### 3. Versioned Installations & Safe Rollback Layout
Tools installed via archive extraction (such as Ngspice) use a versioned directory structure under `~/.esim-tools/`:

```text
~/.esim-tools/ngspice/
├── versions/
│   ├── 47/
│   └── 48/
├── active/
│   └── Spice64/
│       └── bin/
│           └── ngspice.exe
└── metadata.json
```

### 4. Upgrade Verification & Rollback Workflow
When upgrading:
1. Extract candidate version into `versions/<new_version>/`.
2. **Verify executable**: Verify `ngspice.exe` exists in the extracted directory. If verification fails, discard candidate and abort upgrade.
3. **Backup active**: Copy current `active/` directory to `active_backup/`.
4. **Swap & Activate**: Copy `versions/<new_version>/` into `active/` and update `metadata.json`.
5. **Automatic Rollback**: If activation fails, restore `active_backup/` to `active/` and restore `metadata.json`.
6. Cleanup backup directory upon verified success.

### 5. Platform Abstraction Layer (`platform_adapter.py`)
Decouples operating system specifics:
- `WindowsAdapter`: Manages WinGet invocations, PowerShell PATH scripts, and `%LOCALAPPDATA%` / `%ProgramFiles%` path discovery.
- `LinuxAdapter`: Manages POSIX shell scripts and system package manager integrations (`apt`, `dnf`, `pacman`).
