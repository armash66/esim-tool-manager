import json
from pathlib import Path

CONFIG_PATH = Path.home() / ".esim-tools" / "config.json"

DEFAULT_CONFIG = {
    "install_directory": str(Path.home() / ".esim-tools"),
    "auto_update": False,
}


def load_config() -> dict:
    if not CONFIG_PATH.is_file():
        save_config(DEFAULT_CONFIG)
        return dict(DEFAULT_CONFIG)

    try:
        with open(CONFIG_PATH, "r") as f:
            data = json.load(f)

        # Merge with defaults so missing keys fall back smoothly
        config = dict(DEFAULT_CONFIG)
        config.update(data)
        return config
    except Exception as e:
        print(f"Warning: Could not read config file ({e}). Using defaults.")
        return dict(DEFAULT_CONFIG)


def save_config(config: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")


def get_install_dir() -> Path:
    cfg = load_config()
    raw = cfg.get("install_directory", str(Path.home() / ".esim-tools"))
    return Path(raw).expanduser()
