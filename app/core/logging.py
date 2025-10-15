import logging
import json
import time


class JsonFormatter(logging.Formatter):
    # Customizing the log
    def format(self, record: logging.LogRecord) -> str:
        base = {
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "time": int(time.time() * 1000),
        }
        if record.exc_info:
            base["exc_info"] = self.formatException(record.exc_info)
        return json.dump(base, ensure_ascii=False)


def setup_logging(level: str = "INFO") -> None:
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level.upper())
    h = logging.StreamHandler()
    h.setFormatter(JsonFormatter())
    root.addHandler(h)
