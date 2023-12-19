import logging
from abc import ABC, abstractmethod

from .server import Server
from ..core.logger import no_logger


class MessageHandler(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def handle(self, websocket, message):
        pass

    def listen(self, websocket, endpoint) -> str:
        pass

    def clear(self, websocket, endpoint):
        pass


class Manager(ABC):
    def __init__(self,
                 message_handler: MessageHandler,
                 comms: list[Server],
                 logger: logging.Logger = None
                 ):
        self.message_handler = message_handler
        self.comms = comms
        self.logger = logger if logger else no_logger(__name__)

        for comm in comms:
            comm.logger = self.logger

    async def handle(self, websocket, message):
        self.message_handler.handle(websocket, message)

    def start(self):
        for comm in self.comms:
            comm.start()

    def stop(self):
        for comm in self.comms:
            comm.stop()

    def alive(self):
        return all([comm.alive for comm in self.comms])
