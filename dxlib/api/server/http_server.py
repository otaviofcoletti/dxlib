import http.server
import inspect
import json
import queue
import socket
import socketserver
import threading
from urllib.parse import parse_qs, urlparse

from .server import ServerStatus, handle_exceptions_decorator, Server


class ReusableTCPServer(socketserver.TCPServer):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        super().server_bind()


class HttpServer(Server):
    def __init__(self, manager, port=None, config_file=None, logger=None):
        super().__init__(manager, logger)
        self.endpoints = {}

        if not config_file:
            self.set_endpoints()

        self.port = port if port else self._get_free_port()

        self._error = threading.Event()

        self._httpd_server = None
        self._httpd_thread = None

    # def load_config(self, config_file):
    #     with open(config_file, 'r') as file:
    #         config = yaml.safe_load(file)
    #
    #     for method_name, endpoint in config.items():
    #         if hasattr(self.managers, method_name):
    #             self.endpoints[method_name] = endpoint

    def add_endpoint(self, endpoint, callable_func):
        route_name = endpoint["route_name"]
        method = endpoint["method"]
        self.endpoints[route_name] = self.endpoints.get(route_name, {})
        self.endpoints[route_name][method] = {
            "endpoint": endpoint,
            "callable": callable_func,
        }

    def set_endpoints(self):
        for func_name in dir(self.manager):
            attr = self.manager.__class__.__dict__.get(func_name, None)

            if callable(attr) and hasattr(attr, "endpoint"):
                endpoint = attr.endpoint
                # noinspection PyUnresolvedReferences
                callable_func = attr.__get__(self.manager)
                self.add_endpoint(endpoint, callable_func)

            elif isinstance(attr, property):
                if hasattr(attr.fget, "endpoint"):
                    endpoint = attr.fget.endpoint
                    # noinspection PyUnresolvedReferences
                    callable_func = attr.fget.__get__(
                        self.manager, self.manager.__class__
                    )
                    self.add_endpoint(endpoint, callable_func)

                if hasattr(attr.fset, "endpoint"):
                    endpoint = attr.fset.endpoint
                    # noinspection PyUnresolvedReferences
                    callable_func = attr.fset.__get__(
                        self.manager, self.manager.__class__
                    )
                    self.add_endpoint(endpoint, callable_func)

    @staticmethod
    def _get_free_port():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            return s.getsockname()[1]

    def list_endpoints(self):
        endpoint_data = {"message": "Available endpoints:", "endpoints": {}}

        for route_name, endpoint in self.endpoints.items():
            methods_data = {}

            for method, method_endpoint in endpoint.items():
                endpoint = method_endpoint["endpoint"]

                methods_data[method] = {
                    "description": endpoint.get(
                        "description", "No description provided"
                    ),
                    "params": {
                        name: str(typehint)
                        for name, typehint in dict(endpoint.get("params", [])).items()
                        if name != "self"
                    },
                }

            endpoint_data["endpoints"][route_name] = methods_data

        return json.dumps(endpoint_data, indent=4)

    def _serve(self):
        if self._httpd_server is not None:
            raise RuntimeError("Server already started")

        class SimulationManagerHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
            endpoints = self.endpoints
            list_endpoints = self.list_endpoints
            manager = self.manager

            exception_queue = self.exception_queue

            def handle_exception(self, e):
                self.exception_queue.put(e)
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())

            def parse_route(self):
                path_parts = urlparse(self.path)
                route_name = path_parts.path.lstrip("/")
                params = parse_qs(path_parts.query)

                if route_name not in self.endpoints:
                    self.send_response(404)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(
                        json.dumps({"error": "Function not found"}).encode()
                    )
                    return None, None

                return route_name, params

            def parse_endpoint(self, method_endpoint):
                func_callable = (
                    method_endpoint.get("callable", None) if method_endpoint else None
                )
                endpoint = (
                    method_endpoint.get("endpoint", None) if method_endpoint else None
                )

                if endpoint is None:
                    self.send_response(405)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(
                        json.dumps({"error": "Method Not Allowed"}).encode()
                    )

                return func_callable, endpoint

            def call_func(
                self, func_callable: callable, endpoint: dict, params=None, data=None
            ):
                if params is None:
                    params = {}
                if data is None:
                    data = {}

                func_signature = endpoint.get("params", {})

                required_args = [
                    arg
                    for arg, details in func_signature.items()
                    if details.default == inspect.Parameter.empty and arg != "self"
                ]

                missing_args = set(required_args) - set(data.keys() if data else [])

                if missing_args:
                    self.send_response(400)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(
                        json.dumps(
                            {
                                "error": f"Missing arguments",
                                "missing": list(missing_args),
                            }
                        ).encode()
                    )
                    return

                try:

                    class MethodEncoder(json.JSONEncoder):
                        def default(self, obj):
                            if hasattr(obj, "to_json") and callable(obj.to_json):
                                return obj.to_json()
                            return super().default(obj)

                    response = func_callable(**data) if data else func_callable()

                    if isinstance(response, list) and params:
                        response = [
                            item
                            for item in response
                            if all(item.get(k) == v for k, v in params.items())
                        ]

                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(
                        json.dumps(
                            response if response else "ok", cls=MethodEncoder
                        ).encode()
                    )

                except Exception as unknown_error:
                    self.send_response(500)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(unknown_error)}).encode())
                    raise unknown_error

            @handle_exceptions_decorator
            def do_GET(self):
                if self.path == "/":
                    response = self.list_endpoints()
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(response.encode())
                    return

                route_name, params = self.parse_route()
                if route_name is None:
                    return

                method_endpoint = self.endpoints[route_name].get("GET", None)
                func_callable, endpoint = self.parse_endpoint(method_endpoint)

                if endpoint is None:
                    return

                return self.call_func(func_callable, endpoint, params)

            @handle_exceptions_decorator
            def do_POST(self):
                route_name, params = self.parse_route()
                if route_name is None:
                    return

                method_endpoint = self.endpoints[route_name].get("POST", None)
                func_callable, endpoint = self.parse_endpoint(method_endpoint)

                if endpoint is None:
                    return

                content_length = int(self.headers["Content-Length"])
                post_data = None

                if content_length > 0:
                    raw_post_data = self.rfile.read(content_length).decode()
                    try:
                        post_data = json.loads(raw_post_data)
                    except json.JSONDecodeError:
                        self.send_response(400)  # Bad Request
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(
                            json.dumps({"error": "Invalid JSON data received"}).encode()
                        )
                        return

                return self.call_func(func_callable, endpoint, params, post_data)

        SimulationManagerHTTPRequestHandler.server = self

        try:
            with ReusableTCPServer(
                ("", self.port), SimulationManagerHTTPRequestHandler
            ) as self._httpd_server:
                self.logger.info(
                    f"Server started on port {self.port}. Press Ctrl+C to stop"
                )
                self._httpd_server.serve_forever()
        except Exception as e:
            self.logger.error(f"Server error: {e}")
            self._error.set()
            self.exception_queue.put(e)
        except KeyboardInterrupt:
            self.logger.info("Server stopped by user")

    def start(self) -> ServerStatus:
        self.logger.info(f"Server starting on port {self.port}")
        self._httpd_thread = threading.Thread(target=self._serve)
        self._httpd_thread.start()
        self._started.set()
        return ServerStatus.STARTED

    def stop(self) -> ServerStatus:
        if self._error.is_set():
            self.logger.warning(
                "Could not stop server. Server might not have started properly"
            )
            return ServerStatus.ERROR

        self._started.wait()
        self._started.clear()

        self.logger.info("Stopping server")

        if self._httpd_thread is not None:
            self._httpd_thread.join()
        if self._httpd_server is not None:
            self._httpd_server.shutdown()
            self._httpd_server.server_close()
            self._httpd_server = None

        return ServerStatus.STOPPED

    def __del__(self):
        self.stop()
