import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple

from .endpoint import EndpointWrapper, Method, EndpointType


class Handler(ABC):
    def __init__(self, endpoints: Dict = None):
        self._endpoints = endpoints or {}

    @property
    def endpoints(self):
        return self._endpoints

    @abstractmethod
    def set_endpoint(self, endpoint: EndpointWrapper, func: callable):
        pass

    def set_endpoints(self, endpoints: List[Tuple[EndpointWrapper, callable]]):
        if endpoints is None:
            return
        for endpoint, func in endpoints:
            self.set_endpoint(endpoint, func)


class HTTPHandler(Handler, ABC):

    def __init__(self, endpoints: Dict[str, Dict[Method, Tuple[EndpointWrapper, callable]]] = None):
        super().__init__(endpoints)

    @property
    def endpoints(self) -> Dict[str, Dict[Method, Tuple[EndpointWrapper, callable]]]:
        return self._endpoints

    def set_endpoint(self, endpoint: EndpointWrapper, func: callable):
        route_name = endpoint.route_name
        method = endpoint.method
        self.endpoints[route_name] = self.endpoints.get(route_name, {})
        self.endpoints[route_name][method] = (endpoint, func)

    def add_interface(self, interface, endpoint_type: EndpointType = EndpointType.HTTP):
        self.set_endpoints(interface.get_endpoints(endpoint_type))


class WebsocketHandler(Handler):
    def __init__(self, endpoints: Dict[str, Tuple[EndpointWrapper, callable]] = None):
        super().__init__(endpoints)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.websockets: Dict[str, any] = {}

    @property
    def endpoints(self) -> Dict[str, Tuple[EndpointWrapper, callable]]:
        return self._endpoints

    def set_endpoint(self, endpoint: EndpointWrapper, func: callable):
        route_name = endpoint.route_name
        self.endpoints[route_name] = (endpoint, func)

    def add_interface(self, interface, endpoint_type: EndpointType = EndpointType.WEBSOCKET):
        self.set_endpoints(interface.get_endpoints(endpoint_type))

    def listen(self, func, *args, **kwargs):
        route_name = func.endpoint.route_name
        generator = func(*args, **kwargs)

        async def _listen():
            async for message in generator:
                for websocket in self.websockets[route_name]:
                    await websocket.send(json.dumps(message))

        return _listen

    def on_connect(self, websocket: any, endpoint: str):
        if not hasattr(websocket, "send"):
            raise ValueError("Invalid websocket connection")
        if endpoint not in self.endpoints:
            raise ValueError("Invalid endpoint")

        self.websockets[websocket] = endpoint
        endpoint, func = self.endpoints[endpoint]

        # run the function and send message to the client
        func(websocket, endpoint)

    def on_disconnect(self, websocket, endpoint):
        self.logger.info("Websocket connection closed")

    def on_message(self, websocket, endpoint, message):
        if endpoint not in self.endpoints:
            raise ValueError("Invalid endpoint")


# class TCPHandler(Handler):
#     pass
