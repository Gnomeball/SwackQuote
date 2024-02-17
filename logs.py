"""
Quick but reliable logging wrapper that will rotate log files cleanly in our desired formatting.

Only imported by `bot.py`, which calls `init()`, and from then on everything is ready to use.
"""

import logging
import logging.config
import logging.handlers
from pathlib import Path


def init() -> None:
    """Configure `logging` with our handlers of choice."""
    OUTLOG.touch()
    ERRLOG.touch()
    DBGLOG.touch()
    logging.config.dictConfig(LOG_CONFIG)


OUTLOG = Path("out.log")
"Where INFO level logging goes."

ERRLOG = Path("err.log")
"Where ERROR level logging goes."

DBGLOG = Path("dbg.log")
"Where DEBUG level logging goes (when used)."

FILE_CONFIG = {"formatter": "fmt", "maxBytes": 10**6, "backupCount": 5}
"We limit logs to 1MB, and rotate through up to 5 at a time."

LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {"fmt": {"format": "[{asctime}: {name} {levelname}]: {message}", "style": "{"}},
    "handlers": {
        "outfile": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "filename": OUTLOG,
            **FILE_CONFIG,
        },
        "errfile": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "filename": ERRLOG,
            **FILE_CONFIG,
        },
        "debugfile": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "filename": DBGLOG,
            **FILE_CONFIG,
        },
    },
    "root": {"level": "INFO", "handlers": ["outfile", "errfile", "debugfile"]},
}
"We have INFO, ERROR, and DEBUG logging setup, with our formatting."
