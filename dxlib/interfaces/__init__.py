import requests

from .external import *
from .internal import *
from .servers import *
from .servers.endpoint import EndpointWrapper, Method


class Interface:
    def __init__(self, url: str, headers: dict = None):
        self.url = url
        self.headers = headers or {}
        pass

    def request(self, endpoint_wrapper: EndpointWrapper, **kwargs):
        if endpoint_wrapper.method == Method.GET:
            response = requests.get(self.url + endpoint_wrapper.route_name, headers=self.headers, **kwargs)
        elif endpoint_wrapper.method == Method.POST:
            response = requests.post(self.url + endpoint_wrapper.route_name, headers=self.headers, **kwargs)
        elif endpoint_wrapper.method == Method.PUT:
            response = requests.put(self.url + endpoint_wrapper.route_name, headers=self.headers, **kwargs)
        else:
            raise ValueError(f"Method {endpoint_wrapper.method} not supported")

        if endpoint_wrapper.output is not None:
            return endpoint_wrapper.output(response.json())
        else:
            return response.json()
