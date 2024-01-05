import queue
import threading
from abc import ABC, abstractmethod
from enum import Enum

from ..managers.handler import MessageHandler
from ..core.logger import info_logger


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


class Server(ABC):
    def __init__(self, handler: MessageHandler = None, logger=None):
        self.logger = logger if logger else info_logger(__name__)

        self.handler = handler
        self._running = threading.Event()

        self.exception_queue = queue.Queue()
        self.exceptions = ExceptionContext(self)

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
