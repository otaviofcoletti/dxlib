import queue
import socket
import threading
from abc import ABC, abstractmethod
from enum import Enum

from ...core.logger import LoggerMixin


class ServerStatus(Enum):
    ERROR = -1
    STARTED = 0
    STOPPED = 1


def handle_exceptions_decorator(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            self.handle_exception(e)

    return wrapper


class ExceptionContext:
    def __init__(self, server):
        self.server = server

    def __enter__(self):
        return self.server.get_exceptions()

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class Server(ABC, LoggerMixin):
    def __init__(self, logger=None):
        super().__init__(logger=logger)
        self._running = threading.Event()

        self.exception_queue = queue.Queue()
        self.exceptions = ExceptionContext(self)

    @staticmethod
    def _get_free_port():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            return s.getsockname()[1]

    @property
    def alive(self):
        return self._running.is_set()

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    def get_exceptions(self):
        try:
            return self.exception_queue.get_nowait()
        except queue.Empty:
            return None


class ServerManager(ABC, LoggerMixin):
    def __init__(
            self,
            servers: list[Server] = None,
            logger=None,
    ):
        super().__init__(logger)
        if isinstance(servers, Server):
            self.servers = [servers]

        self.set_servers(servers or [])

    def set_servers(self, servers: list[Server]):
        self.servers = servers
        for server in self.servers:
            server.logger = self.logger

    def start(self):
        for server in self.servers:
            server.start()

    def stop(self):
        for server in self.servers:
            server.stop()

    def alive(self):
        alive = all([server.alive for server in self.servers])
        return alive if self.servers else False
