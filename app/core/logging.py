import logging
import sys
from logging.config import dictConfig

dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            # "json": {
            #     "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": %(message)s}',
            #     "datefmt": "%Y-%m-%dT%H:%M:%S",
            # },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "formatter": "default",
            },
            # TODO: 파일 핸들러 추가
        },
        "root": {
            "level": "INFO",
            "handlers": ["console"],
        },
    }
)

logger = logging.getLogger(__name__)
