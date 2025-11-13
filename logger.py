import logging
import sys
from datetime import datetime

from config import settings

CONSOLE_FORMAT = "%(levelname)s | %(name)s | %(message)s"
FILE_FORMAT = (
    "%(asctime)s | %(levelname)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"
)


class CustomFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""

    green = "\x1b[32m"
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    FORMATS = {
        logging.DEBUG: grey + FILE_FORMAT + reset,
        logging.INFO: green + FILE_FORMAT + reset,
        logging.WARNING: yellow + FILE_FORMAT + reset,
        logging.ERROR: red + FILE_FORMAT + reset,
        logging.CRITICAL: bold_red + FILE_FORMAT + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def setup_logging() -> None:
    """
    Configure root logger once at application startup.
    Call this once in main.py before any other imports that use logging.
    """
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG.LEVEL)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.LOG.LEVEL)
    console_handler.setFormatter(CustomFormatter())
    root_logger.addHandler(console_handler)

    # File handler
    logs_dir = settings.LOG.DIR
    logs_dir.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(
        logs_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log", encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(FILE_FORMAT))
    root_logger.addHandler(file_handler)
