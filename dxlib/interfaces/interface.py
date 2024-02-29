from typing import List, Tuple

import requests

from .servers.endpoint import EndpointWrapper, Method, EndpointType


class Interface:
    def __init__(self, base_url: str = None, headers: dict = None):
        self.base_url = base_url
        self.headers = headers or {}

        self.endpoints = {
            wrapper.route_name: wrapper
            for wrapper, _ in self.get_endpoints()
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

    def request(self, endpoint_wrapper: EndpointWrapper = None, route_name: str = None, **kwargs):
        if route_name is None and endpoint_wrapper is None:
            raise ValueError("URL or endpoint_wrapper must be provided")

        if route_name is not None:
            endpoint_wrapper = self.endpoints[route_name]

        url = self.base_url + endpoint_wrapper.route_name

        if endpoint_wrapper.method == Method.GET:
            request = requests.get
        elif endpoint_wrapper.method == Method.POST:
            request = requests.post
        elif endpoint_wrapper.method == Method.PUT:
            request = requests.put
        else:
            raise ValueError(f"Method {endpoint_wrapper.method} not supported")

        response = request(url, headers=self.headers, **kwargs)

        if endpoint_wrapper.output is not None:
            return endpoint_wrapper.output(response.json())
        else:
            return response.json()
