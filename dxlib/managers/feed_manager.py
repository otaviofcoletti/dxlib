from __future__ import annotations

import asyncio
import threading
from typing import Generator, AsyncGenerator

from .generic_manager import GenericManager, GenericMessageHandler
from ..core import no_logger, History


def to_async(subscription: Generator, delay=0.0):
    async def async_subscription():
        for item in subscription:
            yield item
            await asyncio.sleep(delay)
    return async_subscription()


class FeedManager(GenericManager):
    def __init__(self, subscription: AsyncGenerator | Generator | None, port=6000, logger=None):
        super().__init__(None, port, logger)
        if isinstance(subscription, Generator):
            self.subscription = to_async(subscription)
        else:
            self.subscription = subscription

        self._running = threading.Event()

        self.thread = None
        self.logger = no_logger(__name__) if logger is None else logger

        self.message_handler = FeedMessageHandler(self)

    async def handle(self, data):
        snapshot = History(data)
        self.logger.info(f"Sent snapshot: {snapshot}")
        self.message_handler.send_snapshot(snapshot)

    async def _subscribe(self):
        async for data in self.subscription:
            if not self._running.is_set():
                break
            await self.handle(data)
        return

    async def _serve(self):
        if self.subscription:
            await self._subscribe()
            self._running.clear()
        else:
            while self._running.is_set():
                pass

    def start(self):
        super().start()
        if self.thread is None:
            self._running.set()
            self.thread = threading.Thread(target=asyncio.run, args=(self._serve(),))
            self.thread.start()

    def stop(self):
        super().stop()
        self._running.clear()

        if self.thread:
            self.thread.join()
        self.thread = None

    def restart(self):
        self.stop()
        self.start()


class FeedMessageHandler(GenericMessageHandler):
    def __init__(self, manager: FeedManager):
        super().__init__()
        self.manager = manager
        self.connections: list = []

    def connect(self, websocket, endpoint) -> str:
        self.connections.append(websocket)
        return "Connected"

    def send_snapshot(self, snapshot: History):
        message = snapshot.to_json()
        for connection in self.connections:
            self.manager.websocket_server.send_message(connection, message)

    def disconnect(self, websocket, endpoint):
        self.connections.remove(websocket)


def main():
    from dxlib.api import YFinanceAPI
    from ..core import info_logger
    logger = info_logger()

    historical_bars = YFinanceAPI().get_historical_bars(["AAPL"])
    subscription = to_async(historical_bars.iterrows(), delay=0.5)

    feed_manager = FeedManager(subscription, logger=logger)
    feed_manager.start()

    try:
        while feed_manager.is_alive():
            pass
    except KeyboardInterrupt:
        logger.info("User interrupted program")
    finally:
        logger.info("Stopping feed manager")
        feed_manager.stop()


if __name__ == "__main__":
    main()
