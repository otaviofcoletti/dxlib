import http.server
import inspect
import json
import socket
import socketserver
import threading
from inspect import signature
from functools import wraps
from urllib.parse import parse_qs, urlparse

from ..core.logger import no_logger


def endpoint(route_name, description=None):
    def decorator(func):
        @wraps(func)  # This helps preserve function metadata
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        params = signature(func).parameters

        wrapper.endpoint = {
            "route_name": route_name,
            "method_name": func.__name__,
            "params": params,
            "description": description,
        }
        return wrapper
    return decorator


class Server:
    def __init__(self, manager, port=None, config_file=None, logger=None):
        self.logger = logger if logger else no_logger(__name__)

        self.manager = manager
        self.endpoints = {}

        if not config_file:
            self.set_endpoints()

        self.port = port if port else self._get_free_port()

        self._started = threading.Event()
        self._error = threading.Event()

        self._httpd_server = None
        self._httpd_thread = None

    # def load_config(self, config_file):
    #     with open(config_file, 'r') as file:
    #         config = yaml.safe_load(file)
    #
    #     for method_name, endpoint in config.items():
    #         if hasattr(self.manager, method_name):
    #             self.endpoints[method_name] = endpoint

    def set_endpoints(self):
        for method_name in dir(self.manager):
            method = getattr(self.manager, method_name, None)
            if method is not None and callable(method) and hasattr(method, "endpoint"):
                self.endpoints[method.endpoint["route_name"]] = method.endpoint

    @staticmethod
    def _get_free_port():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]

    def _serve(self):
        if self._httpd_server is not None:
            raise RuntimeError("Server already started")

        class SimulationManagerHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
            endpoints = self.endpoints
            manager = self.manager

            def list_endpoints(self):
                endpoint_data = {
                    "message": "Available endpoints:",
                    "endpoints": {route_name: {
                        "description": method_endpoint.get('description', 'No description provided'),
                        "params": method_endpoint.get('params', [])
                    }

                                  for route_name, method_endpoint in self.endpoints.items()}
                }
                return json.dumps(endpoint_data, indent=4)

            def do_GET(self):
                if self.path == "/":
                    response = self.list_endpoints()
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(response.encode())
                    return

                path_parts = urlparse(self.path)
                route_name = path_parts.path.lstrip('/')

                if route_name not in self.endpoints:
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "error": "Not Found"
                    }).encode())

                method_info = self.endpoints[route_name]
                method = getattr(self.manager, method_info.get('method_name'))
                params = parse_qs(path_parts.query)
                signature = method_info.get("params", [])

                required_params = [param for param, details in signature.items()
                                   if details.default == inspect.Parameter.empty and param != 'self']

                missing_params = set(required_params) - set(params.keys())

                if missing_params:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "error": f"Missing parameters",
                        "missing": list(missing_params)
                    }).encode())
                    return

                try:
                    response = method(**{k: v[0] for k, v in params.items() if k in signature.parameters and k != 'self'})
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(response).encode())

                except Exception as e:
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "error": str(e)
                    }).encode())

            def do_POST(self):
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode()

                path_parts = self.path.lstrip('/').split('/')
                method_name = path_parts[0]

                if method_name in self.endpoints:
                    method = getattr(self.manager, method_name)
                    response = method(post_data)
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(response.encode())
                else:
                    self.send_response(404)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b'Not Found')

        SimulationManagerHTTPRequestHandler.server = self

        try:
            with socketserver.TCPServer(("", self.port), SimulationManagerHTTPRequestHandler) as self._httpd_server:
                self._started.set()
                self.logger.info(f"Server started on port {self.port}")
                self._httpd_server.serve_forever()
        except Exception as e:
            print(f"Error starting server: {e}")
            self._error.set()

    def start(self):
        self._httpd_thread = threading.Thread(target=self._serve)
        self._httpd_thread.start()

    def stop(self):
        if self._error.is_set():
            self.logger.warning("Could not stop server. Server might not have started properly.")
            return

        self._started.wait()

        if self._httpd_server is not None:
            self._httpd_server.shutdown()
            self._httpd_server.server_close()
            self._httpd_server = None
        if self._httpd_thread is not None:
            self._httpd_thread.join()

    def __del__(self):
        self.stop()
