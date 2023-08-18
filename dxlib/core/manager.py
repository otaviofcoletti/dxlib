import logging

from .logger import no_logger
from ..api import Server


class GenericManager:
    def __init__(
        self, use_server: bool = False, port: int = None, logger: logging.Logger = None
    ):
        self.logger = logger if logger else no_logger(__name__)
        self.server = Server(self, port, logger=self.logger) if use_server else None

    def start_server(self):
        if self.server is not None:
            self.server.start()

    def stop_server(self):
        if self.server is not None:
            self.server.stop()
