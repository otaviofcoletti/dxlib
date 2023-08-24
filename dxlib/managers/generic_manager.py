import logging

from dxlib.core.logger import no_logger
from dxlib.api import HttpServer, WebSocketServer


class GenericManager:
    def __init__(self,
                 use_server: bool = False,
                 use_websocket: bool = False,
                 port: int = None,
                 logger: logging.Logger = None
    ):
        self.logger = logger if logger else no_logger(__name__)
        self.http = HttpServer(self, port, logger=self.logger) if use_server else None
        self.websocket = WebSocketServer(self, port, logger=self.logger) if use_websocket else None

    def start_http(self):
        if self.http is not None:
            self.http.start()

    def stop_server(self):
        if self.http is not None:
            self.http.stop()

    def start_socket(self):
        if self.websocket is not None:
            self.websocket.start()

    def stop_socket(self):
        if self.websocket is not None:
            self.websocket.stop()

    def stop_servers(self):
        self.stop_server()
        self.stop_socket()
