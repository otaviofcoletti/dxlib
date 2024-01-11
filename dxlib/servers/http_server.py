from __future__ import annotations

import inspect
import json
import socket
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import threading
from urllib.parse import parse_qs, urlparse

from .server import ServerStatus, handle_exceptions_decorator, Server
from .handler import HTTPHandler


class HTTPServer(Server):
    def __init__(
        self, handler: HTTPHandler = None, port=None, logger=None
    ):
        super().__init__(handler, logger)
        self.endpoints = handler.endpoints if handler else {}
        self.port = port if port else self._get_free_port()

        self._httpd_thread = threading.Thread(target=self._serve)
        self._httpd_server: ThreadingHTTPServer | None = None
        self._error = threading.Event()
        self._running = threading.Event()

    def add_endpoints(self, endpoints):
        if endpoints is None:
            return
        for endpoint, func in endpoints:
            self.add_endpoint(endpoint, func)

    def add_endpoint(self, endpoint, callable_func):
        route_name = endpoint["route_name"]
        method = endpoint["method"]
        self.endpoints[route_name] = self.endpoints.get(route_name, {})
        self.endpoints[route_name][method] = {
            "endpoint": endpoint,
            "callable": callable_func,
        }

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
                    "description": endpoint.get("description"),
                    "params": {
                        name: str(typehint)
                        for name, typehint in dict(endpoint.get("params")).items()
                        if name != "self"
                    },
                }

            endpoint_data["endpoints"][route_name] = methods_data

        return json.dumps(endpoint_data, indent=4)

    def _serve(self):
        if self._httpd_server is not None:
            raise RuntimeError("Server already started")

        class HTTPRequestHandler(SimpleHTTPRequestHandler):
            endpoints = self.endpoints
            list_endpoints = self.list_endpoints

            exception_queue = self.exception_queue
            running = self._running

            def handle_exception(self, e):
                self.exception_queue.put(e)
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())

            def parse_route(self):
                path_parts = urlparse(self.path)
                route_name = path_parts.path
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
                func_callable = method_endpoint.get() if method_endpoint else None
                endpoint = method_endpoint.get() if method_endpoint else None

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
                            if hasattr(obj, "to_dict") and callable(obj.to_dict):
                                return obj.to_dict()
                            elif hasattr(obj, "to_json") and callable(obj.to_json):
                                return obj.to_json()
                            else:
                                return super().default(obj)

                    response = func_callable(**data) if data else func_callable()

                    if isinstance(response, list) and params:
                        response = [
                            item
                            for item in response
                            if all(item.get() == v for k, v in params.items())
                        ]

                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(
                        json.dumps(
                            "ok" if response is None else response, cls=MethodEncoder
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

                method_endpoint = self.endpoints[route_name].get()
                func_callable, endpoint = self.parse_endpoint(method_endpoint)

                if endpoint is None:
                    return

                return self.call_func(func_callable, endpoint, params)

            @handle_exceptions_decorator
            def do_POST(self):
                route_name, params = self.parse_route()
                if route_name is None:
                    return

                method_endpoint = self.endpoints[route_name].get()
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

        HTTPRequestHandler.server = self

        try:
            with ThreadingHTTPServer(
                ("", self.port), HTTPRequestHandler
            ) as self._httpd_server:
                self.logger.info(f"Server started. Press Ctrl+C to stop...")
                self._httpd_server.timeout = 1
                while self._running.is_set():
                    self.logger.info("Handling request")
                    self._httpd_server.handle_request()
        except Exception as e:
            self.logger.error(f"Server error: {e}")
            self._error.set()
            self.exception_queue.put(e)
        except KeyboardInterrupt:
            self.logger.info("Server stopped by user")

    def start(self) -> ServerStatus:
        self.logger.info(f"Server starting on port {self.port}")
        self._running.set()
        self._httpd_thread.start()
        return ServerStatus.STARTED

    def stop(self) -> ServerStatus:
        if self._error.is_set():
            self.logger.warning(
                "Could not stop servers. Server might not have started properly"
            )
            return ServerStatus.ERROR

        if not self._running.is_set():
            return ServerStatus.STOPPED

        self.logger.info("Stopping servers")
        self._running.clear()

        if self._httpd_server is not None and self._httpd_server.socket is not None:
            self._httpd_server = None
        if self._httpd_thread is not None and self._httpd_thread.is_alive():
            self._httpd_thread.join()
        self.logger.info("Server stopped")

        return ServerStatus.STOPPED

    def __del__(self):
        self.stop()
