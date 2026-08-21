# eSim Tool Manager User Guide

This guide details command line usage and workflows for `esim-tool-manager`.

## Command Summary

| Command | Description | Example |
|---|---|---|
| `list` | List all tools in registry and basic installation status | `python src/manager.py list` |
| `check` | Run detailed detection checks for core tools | `python src/manager.py check` |
| `doctor` | Run full environment diagnostics & readiness check | `python src/manager.py doctor` |
| `install <tool>` | Install specified tool (KiCad via WinGet, Ngspice via 7z) | `python src/manager.py install ngspice` |
| `update [tool]` | Check for or apply tool updates | `python src/manager.py update kicad` |
| `config` | View or modify tool manager configuration | `python src/manager.py config --set auto_update true` |

---

## Detailed Command Workflows

### 1. Environment Readiness (`doctor`)
Run `doctor` to check all core tools and environment directories:
```bash
python src/manager.py doctor
```
*Output Example:*
```text
eSim Environment Doctor

Core Tools

KiCad
  [+] Installed
  [+] Version: 10.0.5
  [+] Executable available

Ngspice
  [+] Installed
  [+] Version: 47
  [+] Executable available

GHDL
  [-] Not installed

Verilator
  [-] Not installed

Configuration
  [+] Install directory exists (C:\Users\...\.esim-tools)
  [+] Configuration valid

=============================================
Overall Status: NOT READY (missing/broken: GHDL, Verilator)
=============================================
```

---

### 2. Tool Installation (`install`)
Install Ngspice or KiCad:
```bash
python src/manager.py install ngspice
python src/manager.py install kicad
```

---

### 3. Check for Updates (`update`)
Check available updates across tools or update a specific tool:
```bash
python src/manager.py update
python src/manager.py update kicad
```

---

### 4. Manager Configuration (`config`)
View or set configuration settings:
```bash
python src/manager.py config
python src/manager.py config --set auto_update true
```
