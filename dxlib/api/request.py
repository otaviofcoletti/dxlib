import requests

from enum import Enum


class RequestType(Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'


def request(func):
    def wrapper(self, *args, **kwargs):
        self.num_calls += 1
        return func(self, *args, **kwargs)

    return wrapper
#
#
# def endpoint(method, endpoint_uri):
#     def decorator(func):
#         def wrapper(self, *args, **kwargs):
#             url = self.form_url(endpoint_uri)
#             return method(self, url, *args, **kwargs)
#
#         return wrapper
#     return decorator


class Api:
    def __init__(self, api_key, api_secret, base_url, api_version='v1'):
        self.__api_key = api_key
        self.__api_secret = api_secret
        self.base_url = base_url
        self.api_version = api_version

        self.num_calls = 0

    def form_url(self, endpoint_uri):
        return f'{self.base_url}/{self.api_version}/{endpoint_uri}'

    @request
    def get(self, url, headers=None):
        if headers is None:
            headers = {}
        headers.update({
            'APCA-API-KEY-ID': self.__api_key,
            'APCA-API-SECRET-KEY': self.__api_secret
        })

        response = requests.get(
            url,
            headers=headers
        )

        return response.json()

    @request
    def post(self, url, data=None, headers=None):
        if headers is None:
            headers = {}
        headers.update({
            'APCA-API-KEY-ID': self.__api_key,
            'APCA-API-SECRET-KEY': self.__api_secret
        })

        response = requests.post(
            url,
            headers=headers,
            data=data
        )

        return response.json()

    @request
    def put(self, url, data=None, headers=None):
        if headers is None:
            headers = {}
        headers.update({
            'APCA-API-KEY-ID': self.__api_key,
            'APCA-API-SECRET-KEY': self.__api_secret
        })

        response = requests.put(
            url,
            headers=headers,
            data=data
        )

        return response.json()

    @request
    def delete(self, url, data=None, headers=None):
        if headers is None:
            headers = {}
        headers.update({
            'APCA-API-KEY-ID': self.__api_key,
            'APCA-API-SECRET-KEY': self.__api_secret
        })

        response = requests.delete(
            url,
            headers=headers,
            data=data
        )

        return response.json()


class Stream(Api):
    def __init__(self, api_key, api_secret, base_url, api_version='v1'):
        super().__init__(api_key, api_secret, base_url, api_version)

    def test(self):
        self.base_url = 'https://jsonplaceholder.typicode.com/posts/1'
        self.get_stream()

    def get_stream(self):
        s = requests.Session()

        with s.get(self.base_url, headers=None, stream=True) as resp:
            for line in resp.iter_lines():
                if line:
                    print(line)
