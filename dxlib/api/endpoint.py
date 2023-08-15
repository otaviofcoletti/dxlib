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
