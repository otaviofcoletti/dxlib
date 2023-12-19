from abc import ABC

from .server import Server
from ..interfaces import Interface

from .manager import Manager, MessageHandler


class InterfaceMessageHandler(MessageHandler):
    def __init__(self):
        super().__init__()

    def handle(self, websocket, message):
        pass


class InterfaceManager(Manager, ABC):
    def __init__(self,
                 interface: Interface,
                 message_handler: InterfaceMessageHandler,
                 comms: list[Server] = None,
                 *args,
                 **kwargs):
        super().__init__(message_handler, comms, *args, **kwargs)

        self.interface = interface

    async def serve(self):
        while self.alive():
            pass
