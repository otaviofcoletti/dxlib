from __future__ import annotations

from abc import ABC


from ..servers import Server, HttpServer
from ..interfaces import Interface
from .manager import Manager, MessageHandler
from ..servers.endpoint import get_endpoints


class InterfaceMessageHandler(MessageHandler):
    def __init__(self):
        super().__init__()

    def handle(self, websocket, message):
        pass


class InterfaceManager(Manager, ABC):
    def __init__(self,
                 interface: Interface,
                 message_handler: InterfaceMessageHandler = None,
                 comms: list[Server] | Server = None,
                 *args,
                 **kwargs):
        self.interface = interface
        super().__init__(message_handler, comms, *args, **kwargs)

    async def serve(self):
        while self.alive():
            pass

    def add_comm(self, comm: Server = None):
        super().add_comm(comm)

        if isinstance(comm, HttpServer):
            comm.add_endpoints(get_endpoints(self.interface))
