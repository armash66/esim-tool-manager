# eSim Tool Manager Architecture

This document describes the architectural design, component separation, and safety mechanisms of `esim-tool-manager`.

## System Overview

```
                      CLI (manager.py)
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
      Registry (registry.py)          Config (config.py)
            │
      ┌─────┴───────────────┐
      ▼                     ▼
Detectors (detector.py)   Installers / Updaters (installer.py / updater.py)
      │                     │
      └──────────┬──────────┘
                 ▼
    DependencyChecker (dependency.py)
                 │
                 ▼
       Logger (logger.py -> ~/.esim-tools/logs/manager.log)
```

## Core Architectural Design Decisions

### 1. Data Contracts (`ToolInfo` & `DependencyStatus`)
Instead of parsing raw CLI string outputs, detectors return strongly-typed `ToolInfo` dataclasses (`name`, `installed`, `path`, `version`). The `DependencyChecker` transforms these into `DependencyStatus` states (`INSTALLED`, `NOT_INSTALLED`, `BROKEN`, `UNAVAILABLE`).

### 2. Versioned Installations & Safe Rollback Layout
To eliminate destructive overwrites, tools installed via archive extraction (such as Ngspice) use a versioned directory structure under `~/.esim-tools/`:

```
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

### 3. Upgrade Verification & Rollback Workflow
When upgrading:
1. Extract candidate version into `versions/<new_version>/`.
2. **Verify executable**: Verify `ngspice.exe` exists in the extracted directory. If verification fails, discard candidate and abort upgrade.
3. **Backup active**: Copy current `active/` directory to `active_backup/`.
4. **Swap & Activate**: Copy `versions/<new_version>/` into `active/` and update `metadata.json`.
5. **Automatic Rollback**: If activation fails, restore `active_backup/` to `active/` and restore `metadata.json`.
6. Cleanup backup directory upon verified success.

### 4. Non-Blocking Ngspice Version Resolution
On Windows, executing `ngspice.exe --version` launches a GUI console without returning piped stdout. To remain 100% CLI-safe, `NgspiceDetector` reads the exact version from `metadata.json` written by `NgspiceInstaller` at installation time.
