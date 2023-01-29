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
    "handlers": {
        "outfile": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "filename": "/home/SwackQuote/out.log",
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
