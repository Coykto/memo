import json
import logging
import logging.config
from datetime import datetime

from src.core.context import get_request_id


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "level": record.levelname,
            "request_id": get_request_id(),
            "message": record.getMessage(),
            "time": datetime.utcnow().isoformat()[:-3] + "Z",
            "module": record.module,
            "line": record.lineno,
        }

        # Handle extra fields that might contain Unicode
        if hasattr(record, "extra"):
            clean_extra = {}
            for key, value in record.extra.items():
                if isinstance(value, str):
                    clean_extra[key] = value
                elif isinstance(value, (list, dict)):
                    clean_extra[key] = json.dumps(value, ensure_ascii=False)
                else:
                    # Handle potential Unicode in repr() of objects
                    try:
                        clean_extra[key] = json.loads(
                            json.dumps(value, ensure_ascii=False)
                        )
                    except (TypeError, json.JSONDecodeError):
                        clean_extra[key] = str(value)
            log_record.update(clean_extra)

        if record.exc_info:
            import traceback

            formatted = "".join(traceback.format_exception(*record.exc_info))
            log_record["traceback"] = formatted

        return json.dumps(log_record, ensure_ascii=False, default=str)


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
