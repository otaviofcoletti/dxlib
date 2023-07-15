import logging
from rich.logging import RichHandler


class CustomLogger:
    def __init__(self):
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.addHandler(RichHandler(show_time=True))
        self.logger = logger

    def log_info(self, message):
        self.logger.info(message)

    def log_warning(self, message):
        self.logger.warning(message)

    def log_error(self, message):
        self.logger.error(message)

    def log_exception(self, message):
        self.logger.exception(message)
