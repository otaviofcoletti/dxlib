import logging
from abc import ABC

from dxlib.api import HttpServer, WebSocketServer
from dxlib.core.logger import no_logger


class GenericManager:
    def __init__(self,
                 server_port: int = None,
                 websocket_port: int = None,
                 logger: logging.Logger = None
                 ):
        self.logger = logger if logger else no_logger(__name__)
        self.http_server = HttpServer(self, server_port, logger=self.logger) if server_port else None
        self.websocket_server = WebSocketServer(self, websocket_port, logger=self.logger) if websocket_port else None

        self.message_handler = None
        self.connection_handler = None

    def start(self):
        if self.http_server is not None:
            self.http_server.start()
        if self.websocket_server is not None:
            self.websocket_server.start()

    def stop(self):
        if self.http_server is not None:
            self.http_server.stop()
        if self.websocket_server is not None:
            self.websocket_server.stop()

    def is_alive(self):
        return (not self.http_server or self.http_server.is_alive()) and \
               (not self.websocket_server or self.websocket_server.is_alive())


class GenericMessageHandler(ABC):
    def __init__(self):
        pass

    def connect(self, websocket, endpoint) -> str:
        pass

    def handle(self, websocket, message):
        pass

    def disconnect(self, websocket, endpoint):
        pass
