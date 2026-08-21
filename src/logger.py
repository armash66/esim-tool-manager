import logging
from pathlib import Path
from config import get_install_dir

LOG_DIR = get_install_dir() / "logs"
LOG_FILE = LOG_DIR / "manager.log"


def get_logger() -> logging.Logger:
    logger = logging.getLogger("esim_manager")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
