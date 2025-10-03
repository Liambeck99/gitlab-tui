import os
from logging import DEBUG, INFO, FileHandler, Formatter, Logger, getLogger
from pathlib import Path


def get_logger() -> Logger:
    """Setup logging for debug mode."""
    log_dir = Path.home() / ".config" / "gitlab-tui" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "gitlab-tui.log"

    logger = getLogger("gitlab_tui")
    debug_mode_enabled = os.getenv("DEBUG", "").lower() in ["true", "yes", "1"]
    logger.setLevel(DEBUG if debug_mode_enabled else INFO)
    logger.handlers.clear()

    file_handler = FileHandler(log_file)
    file_formatter = Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger
