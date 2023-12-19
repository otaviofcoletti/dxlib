from abc import ABC

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
                 *args,
                 **kwargs):
        super().__init__(message_handler, *args, **kwargs)

        self.interface = interface

    async def serve(self):
        while self.alive():
            pass
