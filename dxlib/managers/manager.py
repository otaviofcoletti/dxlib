import logging
from abc import ABC

from .handler import MessageHandler
from .server import Server
from ..core.logger import info_logger


class Manager(ABC):
    def __init__(self,
                 message_handler: MessageHandler,
                 comms: list[Server] = None,
                 logger: logging.Logger = None
                 ):
        self.message_handler = message_handler
        self.comms = comms if comms else []
        self.logger = logger if logger else info_logger(__name__)

        for comm in self.comms:
            comm.logger = self.logger

    async def handle(self, websocket, message):
        self.message_handler.handle(websocket, message)

    def start(self):
        if not self.comms:
            self.logger.warning("No communicators to start. Skipping...")
            return
        for comm in self.comms:
            comm.start()

    def stop(self):
        for comm in self.comms:
            comm.stop()

    def alive(self):
        return all([comm.alive for comm in self.comms])
