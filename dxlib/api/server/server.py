import queue
import threading
from enum import Enum

from ... import no_logger


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


class Server:
    def __init__(self, manager, logger=None):
        self.logger = logger if logger else no_logger(__name__)

        self.manager = manager
        self._started = threading.Event()

        self.exception_queue = queue.Queue()
        self.exceptions = ExceptionContext(self)

    def is_alive(self):
        return self._started.is_set()

    def get_exceptions(self):
        try:
            return self.exception_queue.get_nowait()
        except queue.Empty:
            return None
