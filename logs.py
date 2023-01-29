import logging.handlers
import logging.config
import logging
from pathlib import Path

def init():
    "Configure `logging` with our handlers of choice."
    logging.config.dictConfig(LOG_CONFIG)

OUTLOG = Path("out.log")
ERRLOG = Path("err.log")
DBGLOG = Path("dbg.log")

OUTLOG.touch()
ERRLOG.touch()
DBGLOG.touch()

FILE_CONFIG = {
    "formatter": "fmt",
    "maxBytes": 10**6,
    "backupCount": 5
}

LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "fmt": {
            "format": "[{asctime}: {name} {levelname}]: {message}",
            "style": "{"
        }
    },
    "handlers": {
        "outfile": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "filename": OUTLOG,
            **FILE_CONFIG
        },
        "errfile": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "filename": ERRLOG,
            **FILE_CONFIG
        },
        "debugfile": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG", # not used for now
            "filename": DBGLOG,
            **FILE_CONFIG
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["outfile", "errfile", "debugfile"]
    }
}
