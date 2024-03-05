from __future__ import annotations

import logging


class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;5;243m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class NoLogger(logging.Logger):
    def __init__(self, name: str = __name__):
        super().__init__(name)
        self.setLevel(logging.NOTSET)


class CriticalLogger(logging.Logger):
    def __init__(self, name: str = __name__):
        super().__init__(name)
        self.setLevel(logging.CRITICAL)


class InfoLogger(logging.Logger):
    def __init__(self, name: str = __name__):
        super().__init__(name)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(CustomFormatter())

        self.setLevel(logging.INFO)
        self.addHandler(ch)


class DebugLogger(logging.Logger):
    def __init__(self, name: str = __name__):
        super().__init__(name)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(CustomFormatter())

        self.setLevel(logging.DEBUG)
        self.addHandler(ch)


class LoggerMixin:
    def __init__(self, logger: logging.Logger | None = None):
        self.logger = logger if logger else NoLogger(__name__)
