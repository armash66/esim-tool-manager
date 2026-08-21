# Toolchain Manifest & Reproducible Environment Guide

The `esim-tool-manager` supports declarative environment modeling via JSON toolchain manifests. This allows developers and CI/CD pipelines to snapshot, verify, plan, and synchronize the eSim toolchain reproducibly.

## Manifest Schema

Manifests use a simple JSON structure (`esim-toolchain.json`):

```json
{
  "schema_version": 1,
  "tools": {
    "kicad": {
      "installed": true,
      "version": "10.0.5",
      "path": "C:\\Users\\...\\AppData\\Local\\Programs\\KiCad\\10.0\\bin\\kicad-cli.exe"
    },
    "ngspice": {
      "installed": true,
      "version": "47",
      "path": "C:\\Users\\...\\.esim-tools\\ngspice\\active\\Spice64\\bin\\ngspice.exe"
    },
    "ghdl": {
      "installed": true,
      "version": "6.0.0",
      "path": "C:\\...\\ghdl.exe"
    },
    "verilator": {
      "installed": true,
      "version": "5.040",
      "path": "C:\\msys64\\mingw64\\bin\\verilator_bin.exe"
    }
  }
}
```

## CLI Operations

### 1. Snapshot (`python src/manager.py snapshot`)
Captures the currently detected toolchain environment and exports it to a manifest file:

```powershell
python src/manager.py snapshot --output esim-toolchain.json
```

### 2. Verification (`python src/manager.py verify`)
Compares actual executable state on the system against a target manifest:

```powershell
python src/manager.py verify --manifest esim-toolchain.json
```

Output:
```text
Toolchain Verification

  kicad        required: 10.0.5     installed: 10.0.5     OK
  ngspice      required: 47         installed: 47         OK
  ghdl         required: 6.0.0      installed: 6.0.0      OK
  verilator    required: 5.040      installed: 5.040      OK

=============================================
Result: MATCH
=============================================
```

### 3. Dry-Run Planning (`python src/manager.py sync --dry-run`)
Previews required installation and upgrade operations without mutating the system:

```powershell
python src/manager.py sync --manifest esim-toolchain.json --dry-run
```

### 4. Synchronization (`python src/manager.py sync`)
Executes required installation and update steps via the registry architecture to bring the environment into compliance:

```powershell
python src/manager.py sync --manifest esim-toolchain.json
```
