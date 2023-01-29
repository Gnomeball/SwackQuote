import logging.handlers
import logging.config
import logging

def init():
    "Configure `logging` with our handlers of choice."
    logging.config.dictConfig(LOG_CONFIG)

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
    "filters": {
        "warnings_and_below": {
            "()": "__main__.filter_below",
            "level": "WARNING"
        }
    },
    "handlers": {
        "outfile": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "filename": "/home/SwackQuote/out.log",
            # "filters": ["warnings_and_below"], # not used for now
            **FILE_CONFIG
        },
        "errfile": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "filename": "/home/SwackQuote/err.log",
            **FILE_CONFIG
        },
        "debugfile": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG", # not used for now
            "filename": "/home/SwackQuote/dbg.log",
            **FILE_CONFIG
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["outfile", "errfile", "debugfile"]
    }
}

def filter_below(level):
    """
    Create a filter to not include higher level/severity logs than the given `level`.
    
    A `filter_below(WARNING)` applied to an `INFO` level logger will only contain `INFO` and `WARNING` logs, and ignores `DEBUG`, `ERROR`, and `CRITICAL` logs.
    
    This makes multi-file logging less redundant, though is best used with tools that can sync up multiple files for easy reading.
    """
    level: int = getattr(logging, level)
    
    def filter(record: logging.LogRecord) -> bool:
        return record.levelno <= level
    
    return filter
