import json
import logging
import logging.config
from datetime import datetime


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "level": record.levelname,
            "message": record.getMessage(),
            "time": datetime.utcnow().isoformat()[:-3] + "Z",
            "module": record.module,
            "line": record.lineno,
        }

        if record.exc_info:
            import traceback

            formatted = "".join(traceback.format_exception(*record.exc_info))
            log_record["traceback"] = formatted

        return json.dumps(log_record)


def setup_logging():
    logging_config = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {"json": {"()": JsonFormatter}},
        "handlers": {
            "console": {"class": "logging.StreamHandler", "formatter": "json"}
        },
        "loggers": {
            "": {"handlers": ["console"], "level": "INFO"},
            "uvicorn": {"handlers": ["console"], "level": "INFO", "propagate": False},
            "uvicorn.access": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "fastapi": {"handlers": ["console"], "level": "INFO", "propagate": False},
        },
    }
    logging.config.dictConfig(logging_config)
    logging.info("Loggig started")
