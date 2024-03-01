import logging
from abc import ABC
from typing import Dict, List, Tuple

from .endpoint import EndpointWrapper, Method, EndpointType


class Handler(ABC):

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


class HTTPHandler(Handler, ABC):

    def add_interface(self, interface, endpoint_type: EndpointType = EndpointType.HTTP):
        self.set_endpoints(interface.get_endpoints(endpoint_type))


class WebsocketHandler(Handler):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)

    def add_interface(self, interface, endpoint_type: EndpointType = EndpointType.WEBSOCKET):
        self.set_endpoints(interface.get_endpoints(endpoint_type))

    def on_connect(self, websocket, endpoint):
        # test if valid websocket connection
        if not hasattr(websocket, "send"):
            raise ValueError("Invalid websocket connection")
        # if not in self.endpoints, close connection
        if endpoint not in self.endpoints:
            raise ValueError("Invalid endpoint")

        self.logger.info("New websocket connection")

    def on_disconnect(self, websocket, endpoint):
        self.logger.info("Websocket connection closed")

    def on_message(self, websocket, endpoint, message):
        pass


class TCPHandler(Handler):
    pass
