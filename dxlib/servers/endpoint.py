import enum
from inspect import signature
from functools import wraps


class Method(enum.Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class Endpoint:
    @staticmethod
    def http(method: Method, route_name: str, description: str = None):
        def decorator(func):  # Do note, func is class bound, not instance bound
            @wraps(func)  # This helps preserve function metadata
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            params = signature(func).parameters

            wrapper.endpoint = {
                "method": method,
                "route_name": route_name,
                "params": params,
            }
            if description is not None:
                wrapper.endpoint["description"] = description
            return wrapper

        return decorator

    @staticmethod
    def websocket(route_name: str, description: str = None):
        def decorator(func):  # Do note, func is class bound, not instance bound
            @wraps(func)  # This helps preserve function metadata
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            params = signature(func).parameters

            wrapper.endpoint = {
                "route_name": route_name,
                "callable": func,
                "params": params,
            }
            if description is not None:
                wrapper.endpoint["description"] = description
            return wrapper

        return decorator


def get_endpoints(instance: object = None):
    endpoints = []

    for func_name in dir(instance):
        attr = instance.__class__.__dict__.get(func_name)

        if callable(attr) and hasattr(attr, "endpoint"):
            endpoint = attr.endpoint
            # noinspection PyUnresolvedReferences
            func = attr.__get__(instance)
            endpoints.append((endpoint, func))

        elif isinstance(attr, property):
            if hasattr(attr.fget, "endpoint"):
                endpoint = attr.fget.endpoint
                # noinspection PyUnresolvedReferences
                func = attr.fget.__get__(instance, instance.__class__)
                endpoints.append((endpoint, func))

            if hasattr(attr.fset, "endpoint"):
                endpoint = attr.fset.endpoint
                # noinspection PyUnresolvedReferences
                func = attr.fset.__get__(instance, instance.__class__)
                endpoints.append((endpoint, func))

    return endpoints
