import os
from pathlib import Path

# Ensure logs directory exists
BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{levelname}] {asctime} {module} {funcName} {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "[{levelname}] {message}",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        
        "app_file": {
            "level": "INFO",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": LOGS_DIR / "app.log",
            "when": "midnight",
            "interval": 1,
            "backupCount": 30,  
            "formatter": "verbose",
            "encoding": "utf-8",
        },
        
        "error_file": {
            "level": "ERROR",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": LOGS_DIR / "error.log",
            "when": "midnight",
            "interval": 1,
            "backupCount": 90,  
            "formatter": "verbose",
            "encoding": "utf-8",
        },
        
      
        "bugsnag": {
            "level": "ERROR",
            "class": "bugsnag.handlers.BugsnagHandler",
        },
    },
    "root": {
        "handlers": ["console", "app_file"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "app_file"],
            "level": "INFO",
            "propagate": False,
        },
        
        "django.request": {
            "handlers": ["console", "error_file"],
            "level": "ERROR",
            "propagate": False,
        },
        
        "django.db.backends": {
            "handlers": ["console"],
            "level": "INFO",  
            "propagate": False,
        },
        
        "django.security": {
            "handlers": ["console", "error_file"],
            "level": "WARNING",
            "propagate": False,
        },
        
        "users": {
            "handlers": ["console", "app_file", "error_file", "bugsnag"],
            "level": "DEBUG",
            "propagate": False,
        },
        
        "swaggerwithdjango": {
            "handlers": ["console", "app_file", "error_file", "bugsnag"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
