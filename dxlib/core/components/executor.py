from __future__ import annotations

from typing import Generator, AsyncGenerator

import pandas as pd

from .history import History, HistorySchema, SignalSchema
from .inventory import Inventory
from .strategy import Strategy
from ...logger import LoggerMixin


class Executor(LoggerMixin):
    def __init__(
            self,
            strategy: Strategy = None,
            position: Inventory = None,
            input_scheme: HistorySchema = None,
            output_scheme: HistorySchema = None,
            logger=None,
    ):
        super().__init__(logger)
        self.strategy = strategy
        self.position = position

        if input_scheme is None:
            input_scheme = HistorySchema()
        self.input_scheme = input_scheme

        if output_scheme is None:
            output_scheme = SignalSchema(input_scheme.levels, fields=["signal"], security_manager=input_scheme.security_manager)
        self.output_scheme = output_scheme

        self._history = History(scheme=input_scheme)

    @property
    def history(self):
        return self._history

    @history.setter
    def history(self, value: History):
        self._history = value

    def run(
            self,
            obj: History | Generator | AsyncGenerator,
            in_place: bool = False,
    ) -> pd.Series | Generator | AsyncGenerator | None:
        if obj is None:
            raise ValueError("Cannot run strategy on None")
        if self.strategy is None:
            raise ValueError("No strategy set")

        if not in_place:
            self._history = History(scheme=self.input_scheme)

        if isinstance(obj, History):
            return self._consume(obj)
        elif isinstance(obj, Generator):
            return self._consume_sync(obj)
        elif isinstance(obj, AsyncGenerator):
            return self._consume_async(obj)

    def _consume(self, obj: History) -> History:
        signals = History(scheme=self.output_scheme)

        try:
            for idx, bar in obj:
                signal = self._consume_bar(idx, bar)
                signals.add(signal)
        except Exception as e:
            self.logger.exception(e)
            raise e
        finally:
            return signals

    def _consume_sync(self, obj: Generator):
        try:
            for bar in obj:
                idx = bar[0]
                bar_df = bar[1]
                signals = self._consume_bar(idx, bar_df)
                yield signals
        finally:
            return

    async def _consume_async(self, obj: AsyncGenerator):
        try:
            async for bar in obj:
                idx = bar[0]
                bar_df = bar[1]
                signals = self._consume_bar(idx, bar_df)
                yield signals
        finally:
            return

    def _consume_bar(self, idx, bar) -> pd.Series:
        self._history.add((idx, bar))
        signals = self.strategy.execute((idx, bar), self.position, self._history)
        return signals
