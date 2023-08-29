import logging

from dxlib.api import HttpServer, WebSocketServer
from dxlib.core.logger import no_logger


class GenericManager:
    def __init__(self,
                 use_server: bool = False,
                 use_websocket: bool = False,
                 server_port: int = None,
                 websocket_port: int = None,
                 logger: logging.Logger = None
                 ):
        self.logger = logger if logger else no_logger(__name__)
        self.server = HttpServer(self, server_port, logger=self.logger) if use_server else None
        self.websocket = WebSocketServer(self, websocket_port, logger=self.logger) if use_websocket else None

    def start_server(self):
        if self.server is not None:
            self.server.start()

    def stop_server(self):
        if self.server is not None:
            self.server.stop()

    def start_websocket(self):
        if self.websocket is not None:
            self.websocket.start()

    def stop_websocket(self):
        if self.websocket is not None:
            self.websocket.stop()

    def start(self):
        if self.server is not None:
            self.start_server()
        if self.websocket is not None:
            self.start_websocket()

    def stop(self):
        self.stop_server()
        self.stop_websocket()
