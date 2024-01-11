from abc import ABC
from typing import Dict

from .endpoint import Endpoint, get_endpoints


class Handler(ABC):
    async def handle(self, *args, **kwargs):
        pass


class HTTPHandler(Handler, ABC):
    def __init__(self, endpoints: Dict[Endpoint, callable]):
        self._endpoints: Dict[Endpoint, callable] = endpoints

    @property
    def endpoints(self) -> Dict[Endpoint, callable]:
        return get_endpoints(self)


class WebsocketHandler(Handler):
    def connect(self, websocket, endpoint):
        pass

    def disconnect(self, websocket, endpoint):
        pass

    def handle(self, websocket, endpoint, message):
        pass


class TCPHandler(Handler):
    pass
