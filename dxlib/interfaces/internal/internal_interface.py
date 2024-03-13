from abc import ABC
from typing import List, Tuple, AsyncGenerator

import requests
import websocket

from ..servers.endpoint import EndpointType, EndpointWrapper, Method


class InternalInterface(ABC):

    def __init__(self, interface_url: str = None, headers: dict = None):
        self.interface_url = interface_url
        self.headers = headers or {}

        self.endpoints = {
            (endpoint_wrapper.route_name, endpoint_wrapper.method): endpoint_wrapper
            for endpoint_wrapper, _ in self.get_endpoints()
        }

    def get_endpoints(self, endpoint_type: EndpointType = None) -> List[Tuple[EndpointWrapper, callable]]:
        endpoints = []

        for func_name in dir(self):
            attr = self.__class__.__dict__.get(func_name)

            if callable(attr) and hasattr(attr, "endpoint") and (
                    endpoint_type is None or attr.endpoint.endpoint_type == endpoint_type):
                endpoint = attr.endpoint
                # noinspection PyUnresolvedReferences
                func = attr.__get__(self)
                endpoints.append((endpoint, func))

            elif isinstance(attr, property):
                if hasattr(attr.fget, "endpoint"):
                    endpoint = attr.fget.endpoint
                    if endpoint_type is not None and endpoint.endpoint_type != endpoint_type:
                        continue
                    # noinspection PyUnresolvedReferences
                    func = attr.fget.__get__(self, self.__class__)
                    endpoints.append((endpoint, func))

                if hasattr(attr.fset, "endpoint"):
                    endpoint = attr.fset.endpoint
                    if endpoint_type is not None and endpoint.endpoint_type != endpoint_type:
                        continue
                    # noinspection PyUnresolvedReferences
                    func = attr.fset.__get__(self, self.__class__)
                    endpoints.append((endpoint, func))

        return endpoints

    def request(self, function: any, *args, **kwargs):
        if self.interface_url is None:
            raise ValueError("URL for interfacing must be provided on interface creation")

        wrapper: EndpointWrapper = function.endpoint

        route = wrapper.route_name
        url = self.interface_url + route

        method = wrapper.method
        if method == Method.GET:
            request = requests.get
        elif method == Method.POST:
            request = requests.post
        elif method == Method.PUT:
            request = requests.put
        else:
            raise ValueError(f"Method {method} not supported")

        response = request(url, headers=self.headers, *args, **kwargs)

        if response.status_code != 200:
            raise ValueError(f"Request failed with status code {response.text}")

        if wrapper and wrapper.output is not None:
            return wrapper.output(response.json())
        else:
            return response.json()

    def listen(self, function: any, *args, **kwargs) -> AsyncGenerator:
        if self.interface_url is None:
            raise ValueError("URL for interfacing must be provided on interface creation")

        wrapper: EndpointWrapper = function.endpoint

        route = wrapper.route_name
        url = self.interface_url + route

        # no method since this is a socket
        if wrapper.endpoint_type == EndpointType.WEBSOCKET:
            # return an async generator using the websocket with recv
            ws = websocket.create_connection(url)

            async def websocket_recv():
                while True:
                    yield ws.recv()

            return websocket_recv()
        elif wrapper.endpoint_type == EndpointType.TCP:
            raise NotImplementedError("TCP not supported yet")
        else:
            raise ValueError(f"Endpoint type {wrapper.endpoint_type} not supported")
