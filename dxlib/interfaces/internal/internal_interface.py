import asyncio
import json
import time
from abc import ABC
from socket import socket
from typing import List, Tuple, AsyncGenerator

import requests
import websocket

from ..servers.endpoint import EndpointScheme, EndpointWrapper, Method


class InternalInterface(ABC):

    def __init__(self, host: str = None, headers: dict = None):
        self.host = host
        self.headers = headers or {}

        self.endpoints = {
            (endpoint_wrapper.route_name, endpoint_wrapper.method): endpoint_wrapper
            for endpoint_wrapper, _ in self.get_endpoints()
        }

    def get_endpoints(self, endpoint_scheme: EndpointScheme = None) -> List[Tuple[EndpointWrapper, callable]]:
        endpoints = []

        for func_name in dir(self):
            attr = self.__class__.__dict__.get(func_name)

            if callable(attr) and hasattr(attr, "endpoint") and (
                    endpoint_scheme is None or attr.endpoint.endpoint_scheme == endpoint_scheme):
                endpoint = attr.endpoint
                # noinspection PyUnresolvedReferences
                func = attr.__get__(self)
                endpoints.append((endpoint, func))

            elif isinstance(attr, property):
                if hasattr(attr.fget, "endpoint"):
                    endpoint = attr.fget.endpoint
                    if endpoint_scheme is not None and endpoint.endpoint_scheme != endpoint_scheme:
                        continue
                    # noinspection PyUnresolvedReferences
                    func = attr.fget.__get__(self, self.__class__)
                    endpoints.append((endpoint, func))

                if hasattr(attr.fset, "endpoint"):
                    endpoint = attr.fset.endpoint
                    if endpoint_scheme is not None and endpoint.endpoint_scheme != endpoint_scheme:
                        continue
                    # noinspection PyUnresolvedReferences
                    func = attr.fset.__get__(self, self.__class__)
                    endpoints.append((endpoint, func))

        return endpoints

    def make_url(self, wrapper: EndpointWrapper, port: int):
        return f"{wrapper.endpoint_scheme.value}://{self.host}:{port}{wrapper.route_name}"

    def request(self, function: any, port: int, *args, **kwargs):
        if self.host is None:
            raise ValueError("URL for interfacing must be provided on interface creation")

        wrapper: EndpointWrapper = function.endpoint
        url = self.make_url(wrapper, port)

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

    @staticmethod
    def _listen_websocket(wrapper: EndpointWrapper, url: str, retry=0) -> Tuple[websocket.WebSocket, AsyncGenerator]:
        ws = None
        for _ in range(retry + 1):
            try:
                ws = websocket.create_connection(url)
                break
            except (ConnectionRefusedError, OSError):
                time.sleep(5)

        if ws is None:
            raise ConnectionRefusedError(f"Could not connect to {url}")

        async def websocket_recv():
            while not ws.connected:
                await asyncio.sleep(0.1)

            try:
                if wrapper and wrapper.output is not None:
                    while ws.connected:
                        yield wrapper.output(json.loads(ws.recv()))
                else:
                    while ws.connected:
                        yield ws.recv()
                return
            except Exception as e:
                raise e
            except KeyboardInterrupt:
                pass
            finally:
                ws.close()

        return ws, websocket_recv()

    def listen(self, function: any, port: int, retry=0) -> Tuple[socket | websocket.WebSocket, AsyncGenerator]:
        if self.host is None:
            raise ValueError("URL for interfacing must be provided on interface creation")

        wrapper: EndpointWrapper = function.endpoint
        url = self.make_url(wrapper, port)

        if wrapper.endpoint_scheme == EndpointScheme.WEBSOCKET:
            return self._listen_websocket(wrapper, url, retry)
        elif wrapper.endpoint_scheme == EndpointScheme.TCP:
            raise NotImplementedError("TCP not supported yet")
        else:
            raise ValueError(f"Endpoint type {wrapper.endpoint_scheme} not supported")
