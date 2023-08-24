import asyncio
import threading
import time
from typing import AsyncGenerator, Generator


class Api:
    def __init__(self):
        pass
        self.n = 100

    async def stream_bars(self) -> AsyncGenerator:
        for i in range(self.n):
            await asyncio.sleep(0.01)
            yield i

    def get_bars(self) -> Generator:
        for i in range(self.n):
            time.sleep(0.01)
            yield i


class History:
    def __init__(self):
        self._bars = []

    @property
    def bars(self):
        return self._bars

    @bars.setter
    def bars(self, value):
        self._bars = value

    def __add__(self, bars):
        if isinstance(bars, list):
            self._bars.extend(bars)
        else:
            self._bars.append(bars)
        return self


class Portfolio:
    def __init__(self):
        self.position = 0

    def __add__(self, other):
        self.position += other
        print("Order executed: ", other)
        return self


class Manager:
    def __init__(self, strategy):
        self.strategy = strategy

        self.portfolios: list[Portfolio] = []
        self.signals = []
        self.history = History()

        self.running = False
        self.thread = None

    def register(self, portfolio):
        self.portfolios.append(portfolio)

    def execute(self):
        position = [portfolio.position for portfolio in self.portfolios]
        signals = self.strategy.execute(self.history, position)

        for portfolio in self.portfolios:
            portfolio += signals

        return signals

    async def _async_consume(self, subscription: AsyncGenerator | Generator):
        async for bars in subscription:
            self.history += bars
            generated_signals = self.execute()
            self.signals.append(generated_signals)
        self.running = False
        return self.signals

    def _consume(self, subscription: Generator):
        for bars in subscription:
            self.history += bars
            generated_signals = self.execute()
            self.signals.append(generated_signals)
        self.running = False
        return self.signals

    def stop(self):
        if self.running:
            self.running = False
        if self.thread:
            self.thread.join()

    def run(self, subscription: AsyncGenerator | Generator, threaded=False):
        if threaded:
            if isinstance(subscription, Generator):
                self.thread = threading.Thread(target=self._consume, args=(subscription,))
            else:
                self.thread = threading.Thread(target=asyncio.run, args=(self._async_consume(subscription),))
            self.thread.start()
            self.running = True
        else:
            if isinstance(subscription, Generator):
                self._consume(subscription)
            else:
                asyncio.run(self._async_consume(subscription))
        return self.signals


def main():
    api = Api()

    class Strategy:
        def execute(self, history, position):
            return 1 if history.bars[-1] > 50 else -1

    manager = Manager(Strategy())
    manager.register(Portfolio())

    signal_history = manager.run(api.stream_bars(), threaded=True)

    while manager.running:
        time.sleep(0.1)
    print(signal_history)


if __name__ == "__main__":
    main()
