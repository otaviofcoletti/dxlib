import enum
from dataclasses import dataclass
from functools import wraps
from inspect import signature


class EndpointType(enum.Enum):
    HTTP = "HTTP"
    WEBSOCKET = "WEBSOCKET"
    TCP = "TCP"


class Method(enum.Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


@dataclass
class EndpointWrapper:

    def __init__(self,
                 endpoint_type: EndpointType,
                 route_name: str,
                 method: Method = None,
                 description: str = None,
                 params: dict = None,
                 func: callable = None,
                 output: any = None):
        self.endpoint_type = endpoint_type
        self.route_name = route_name
        self.method = method
        self.description = description
        self.params = params or {}
        self.func = func
        self.output = output

    endpoint_type: EndpointType
    route_name: str
    method: Method = None
    description: str = None
    params: dict = None
    func: callable = None
    output: any = None


class Endpoint:

    @staticmethod
    def http(method: Method, route_name: str, description: str = None, output: any = None):
        def decorator(func):  # Do note, here func is class bound, not instance bound
            @wraps(func)  # This helps preserve function metadata
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            params = signature(func).parameters

            wrapper.endpoint = EndpointWrapper(
                EndpointType.HTTP,
                route_name,
                method=method,
                params=dict(params),
                output=output,
            )

            if description is not None:
                wrapper.endpoint.description = description
            return wrapper

        return decorator

    @staticmethod
    def websocket(route_name: str, description: str = None):
        def decorator(func):  # Do note, here func is class bound, not instance bound
            @wraps(func)  # This helps preserve function metadata
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            params = signature(func).parameters

            wrapper.endpoint = EndpointWrapper(
                EndpointType.WEBSOCKET,
                route_name,
                params=dict(params),
                output=None,
            )
            if description is not None:
                wrapper.endpoint.description = description
            return wrapper

        return decorator
