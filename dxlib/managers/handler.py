from abc import ABC, abstractmethod


class MessageHandler(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def handle(self, websocket, endpoint, message):
        pass

    def connect(self, websocket, endpoint):
        pass

    def disconnect(self, websocket, endpoint):
        pass

    def listen(self, websocket, endpoint) -> str:
        pass

    def clear(self, websocket, endpoint):
        pass
