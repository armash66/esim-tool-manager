# eSim Tool Manager — User Guide

## 1. Prerequisites

### Supported Operating Systems
- **Windows**: Primary target platform (tested on Windows 10/11 64-bit).
- **Linux**: Supported using the system package manager where supported.

### Python Requirements
- **Python 3.10+** (with Tkinter included).

### Dependencies
Install project dependencies using:

```powershell
python -m pip install -r requirements.txt
```

The required packages (`packaging`, `py7zr`, `pytest`) are installed automatically.

### External Tool Prerequisites (Windows)
- **WinGet** (Windows Package Manager / App Installer): Used for KiCad and GHDL.
- **MSYS2** (Optional): Provides native `pacman` binaries for Verilator.

### Permissions
- The manager runs as a standard user process. Elevated Administrator prompts (UAC) appear only if required by specific package installer subprocesses.

---

## 2. Installation & Setup

1. Clone the repository:
   ```powershell
   git clone https://github.com/armash66/esim-tool-manager.git
   cd esim-tool-manager
   ```

2. Create and activate virtual environment (PowerShell):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```

---

## 3. Launching the GUI

Start the Tkinter Desktop GUI:

```powershell
python src/manager.py gui
```

### GUI Components
- **Tools Table**: Lists managed tools, status (`Installed`, `Not installed`), version, and path.
- **Toolbar**:
  - **Refresh**: Re-scans disk for tool executables.
  - **Open eSim**: Launches eSim application if detected on system PATH.
  - **Doctor Diagnostics**: Opens toolchain environment health check.
  - **Install Selected**: Installs the selected tool.
  - **Install All**: Sequentially installs all missing tools.
  - **Uninstall Selected**: Removes the selected tool.
  - **Check Updates**: Checks upstream repositories for newer versions.
  - **Path Environment**: Displays binary directories and PATH export snippets.
  - **Configuration**: Displays active installation directory settings.
- **Activity Log**: Displays output logs for performed operations.

---

## 4. Managing Tools (CLI & GUI)

### CLI Commands

| Action | Command |
|---|---|
| List status | `python src/manager.py list` |
| Detailed status & paths | `python src/manager.py check` |
| Install tool | `python src/manager.py install <kicad\|ngspice\|ghdl\|verilator>` |
| Install all missing tools | `python src/manager.py install all` |
| Uninstall tool | `python src/manager.py uninstall <tool>` |
| Check environment PATH | `python src/manager.py env` |
| View / set config | `python src/manager.py config [--set key val]` |

*Note: After an installer runs, the manager checks that the executable binary is actually available on disk before confirming success.*

---

## 5. Checking Updates

Check available updates for all tools:

```powershell
python src/manager.py update
```

Or for a specific tool:

```powershell
python src/manager.py update kicad
```

### Reported States:
- **`Up to date (<version>)`**: Installed version is current.
- **`Update available (<installed> → <latest>)`**: A newer version is available.
- **`Unable to determine latest version`**: Network or package manager query failed.
- **`Not installed`**: Tool is missing.

---

## 6. Diagnostics

Run environment health diagnostics:

```powershell
python src/manager.py doctor
```

Outputs overall state:
- `Toolchain Status: READY` (all core tools installed and functional)
- `Toolchain Status: INCOMPLETE` (one or more tools missing or broken)

For machine-readable JSON output:

```powershell
python src/manager.py doctor --json
```

---

## 7. Toolchain Manifest, Dry Run & Sync

### Snapshot State
Save the current toolchain state to a JSON manifest:

```powershell
python src/manager.py snapshot --output esim-toolchain.json
```

### Verify Environment
Compare active tool versions against target manifest requirements:

```powershell
python src/manager.py verify --manifest esim-toolchain.json
```

### Dry Run
Preview planned installation or upgrade actions without modifying the filesystem:

```powershell
python src/manager.py install all --dry-run
python src/manager.py sync --manifest esim-toolchain.json --dry-run
```

### Synchronize Environment
Bring the environment into compliance with a manifest:

```powershell
python src/manager.py sync --manifest esim-toolchain.json
```

---

## 8. Troubleshooting

| Symptom | Cause | Solution |
|---|---|---|
| **Tool listed as `Not installed` after installer finished** | Binary not found in expected path | Run `python src/manager.py check` to trigger a fresh search. |
| **WinGet reports installed but binary is missing** | Stale WinGet package registration | Re-run `python src/manager.py install kicad` to repair/reinstall the installation. |
| **UAC prompt cancelled** | Subprocess permission request denied | Re-run command and accept UAC elevation prompt. |
| **Tool installed but missing from shell PATH** | Directory not in system PATH | Run `python src/manager.py env` to view export commands. |
| **`Unable to determine latest version`** | Package manager query failed | Check network connection or package manager availability. |
| **Ngspice extraction fails** | Missing release archive | Ensure `downloads/ngspice-47_64.7z` exists. |

---

## 9. Running Tests

Run the automated test suite:

```powershell
pytest -v
```

A successful run should report that all tests passed.

---

## 10. Quick Reference

| Action | Command |
|---|---|
| **Launch Desktop GUI** | `python src/manager.py gui` |
| **List Status** | `python src/manager.py list` |
| **Detailed Check** | `python src/manager.py check` |
| **Doctor Check** | `python src/manager.py doctor` |
| **Doctor Check (JSON)** | `python src/manager.py doctor --json` |
| **Install Tool** | `python src/manager.py install <tool>` |
| **Install All Missing** | `python src/manager.py install all` |
| **Install All (Dry Run)** | `python src/manager.py install all --dry-run` |
| **Check Updates** | `python src/manager.py update` |
| **Snapshot Toolchain** | `python src/manager.py snapshot --output esim-toolchain.json` |
| **Verify Manifest** | `python src/manager.py verify --manifest esim-toolchain.json` |
| **Sync Manifest** | `python src/manager.py sync --manifest esim-toolchain.json` |
| **Sync Manifest (Dry Run)** | `python src/manager.py sync --manifest esim-toolchain.json --dry-run` |
| **Run Pytest Suite** | `pytest -v` |
