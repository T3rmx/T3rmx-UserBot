import logging
import os
from logging.handlers import RotatingFileHandler

LOG_FILE = os.environ.get("T3RMX_LOG_FILE", "logs/t3rmx.log")
_FORMAT = "[%(levelname)s- %(asctime)s]- %(name)s- %(message)s- %(filename)s- %(lineno)d"

logging.basicConfig(
    format=_FORMAT,
    level=logging.INFO,
    datefmt="%H:%M:%S",
)


def get_log_file_path() -> str:
    """Return the on-disk log file path (created on first use)."""
    path = os.path.abspath(LOG_FILE)
    parent = os.path.dirname(path)
    try:
        os.makedirs(parent, exist_ok=True)
    except Exception:
        pass
    return path


def _attach_file_handler() -> None:
    try:
        path = get_log_file_path()
        handler = RotatingFileHandler(
            path,
            maxBytes=2 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8",
        )
        handler.setFormatter(logging.Formatter(_FORMAT, datefmt="%H:%M:%S"))
        handler.setLevel(logging.INFO)
        root = logging.getLogger()
        if not any(
            isinstance(h, RotatingFileHandler)
            and getattr(h, "baseFilename", None) == os.path.abspath(path)
            for h in root.handlers
        ):
            root.addHandler(handler)
    except Exception:
        # Logging to stdout must keep working even if the filesystem is read-only.
        pass


_attach_file_handler()


def read_log_text(max_bytes: int = 180000) -> str:
    """Read the tail of the log file without exposing any secrets in code."""
    try:
        path = get_log_file_path()
        if not os.path.isfile(path):
            return ""
        with open(path, "rb") as handle:
            handle.seek(0, os.SEEK_END)
            size = handle.tell()
            handle.seek(max(0, size - max_bytes))
            data = handle.read()
        return data.decode("utf-8", errors="replace")
    except Exception:
        return ""
