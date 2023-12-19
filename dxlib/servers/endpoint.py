from inspect import signature
from functools import wraps


class Endpoint:
    @staticmethod
    def get(route_name, description=None):
        def decorator(func):  # Do note, func is class bound, not instance bound
            @wraps(func)  # This helps preserve function metadata
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            params = signature(func).parameters

            wrapper.endpoint = {
                "method": "GET",
                "route_name": route_name,
                "params": params,
                "description": description,
            }
            return wrapper

        return decorator

    @staticmethod
    def post(route_name, description=None):
        def decorator(func):  # Do note, func is class bound, not instance bound
            @wraps(func)  # This helps preserve function metadata
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            params = signature(func).parameters

            wrapper.endpoint = {
                "method": "POST",
                "route_name": route_name,
                "callable": func,
                "params": params,
                "description": description,
            }
            return wrapper

        return decorator


def get_endpoints(instance):
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
                func = attr.fget.__get__(
                    instance, instance.__class__
                )
                endpoints.append((endpoint, func))

            if hasattr(attr.fset, "endpoint"):
                endpoint = attr.fset.endpoint
                # noinspection PyUnresolvedReferences
                func = attr.fset.__get__(
                    instance, instance.__class__
                )
                endpoints.append((endpoint, func))

    return endpoints
