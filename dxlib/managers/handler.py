from abc import ABC, abstractmethod


class MessageHandler(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def handle(self, websocket, message):
        pass

    def listen(self, websocket, endpoint) -> str:
        pass

    def clear(self, websocket, endpoint):
        pass
