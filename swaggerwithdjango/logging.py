LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{levelname}] {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "[{levelname}] {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "bugsnag": {
            "level": "ERROR",
            "class": "bugsnag.handlers.BugsnagHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "users": {
            "handlers": ["console", "bugsnag"],
            "level": "DEBUG",
            "propagate": False,
        },
        "swaggerwithdjango": {
            "handlers": ["console", "bugsnag"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
