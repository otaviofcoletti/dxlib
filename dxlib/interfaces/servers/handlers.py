from abc import ABC
from typing import Dict, List, Tuple

from dxlib.interfaces.internal.internal_interface import Interface
from dxlib.interfaces.servers.endpoint import EndpointWrapper, Method, EndpointType


class Handler(ABC):
    async def handle(self, *args, **kwargs):
        pass


class HTTPHandler(Handler, ABC):
    def __init__(self, endpoints: Dict[str, Dict[Method, Tuple[EndpointWrapper, callable]]] = None):
        self._endpoints = endpoints or {}

    @property
    def endpoints(self) -> Dict[str, Dict[Method, Tuple[EndpointWrapper, callable]]]:
        return self._endpoints

    def set_endpoints(self, endpoints: List[Tuple[EndpointWrapper, callable]]):
        if endpoints is None:
            return
        for endpoint, func in endpoints:
            self.set_endpoint(endpoint, func)

    def set_endpoint(self, endpoint: EndpointWrapper, func: callable):
        route_name = endpoint.route_name
        method = endpoint.method
        self.endpoints[route_name] = self.endpoints.get(route_name, {})
        self.endpoints[route_name][method] = (endpoint, func)

    def add_interface(self, interface: Interface, endpoint_type: EndpointType = EndpointType.HTTP):
        self.set_endpoints(interface.get_endpoints(endpoint_type))


class WebsocketHandler(Handler):
    def connect(self, websocket, endpoint):
        pass

    def disconnect(self, websocket, endpoint):
        pass

    def handle(self, websocket, endpoint, message):
        pass


class TCPHandler(Handler):
    pass
