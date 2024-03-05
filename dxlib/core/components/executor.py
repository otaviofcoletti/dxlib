from __future__ import annotations

from typing import Generator, AsyncGenerator

import pandas as pd

from .history import History, Schema
from .inventory import Inventory
from .strategy import Strategy
from ..logger import LoggerMixin


class Executor(LoggerMixin):
    def __init__(
            self,
            strategy: Strategy = None,
            position: Inventory = None,
            logger=None,
    ):
        super().__init__(logger)
        self.strategy = strategy
        self.position = position

    def _run(self,
             obj: History | Generator | AsyncGenerator,
             output_history: History,
             input_schema: Schema = None,
             history_log: History = None
             ):
        if isinstance(obj, History):
            return self._consume(obj, output_history, history_log)
        elif isinstance(obj, Generator):
            return self._consume_sync(obj, input_schema, history_log)
        elif isinstance(obj, AsyncGenerator):
            return self._consume_async(obj, input_schema, history_log)

    def run(
            self,
            obj: History | Generator | AsyncGenerator,
            output_history: History = None,
            input_schema: Schema = None,
            log_history: History = None,
    ) -> pd.Series | Generator | AsyncGenerator | None:
        if obj is None:
            raise ValueError("Cannot run strategy on None")
        if self.strategy is None:
            raise ValueError("No strategy set")

        if not isinstance(obj, History) and (input_schema is None):
            raise ValueError("Missing input format for non-History object")

        if output_history is None:
            schema = obj.schema if isinstance(obj, History) else input_schema
            output_schema = Schema(
                levels=schema.levels,
                fields=["signal"],
                security_manager=schema.security_manager
            )
            output_history = History(schema=output_schema)

        return self._run(obj, output_history, input_schema, log_history)

    def _consume_observation(self, observation, output_history, log_history):
        log_history.add(observation)
        signals = self.strategy.execute(observation, self.position, log_history)
        output_history.add(signals)
        return signals

    def _consume(self, input_history: History, output_history: History, log_history: History = None) -> History:
        if log_history is None:
            log_history = History(schema=input_history.schema)
        try:
            for observation in input_history:
                self._consume_observation(observation, output_history, log_history)
        except Exception as e:
            self.logger.exception(e)
            raise e
        finally:
            return output_history

    def _consume_sync(self, input_generator: Generator, input_schema: Schema, log_history: History = None) -> Generator:
        if log_history is None:
            log_history = History(schema=input_schema)
        try:
            for observation in input_generator:
                yield self._consume_observation(observation, log_history, log_history)
        except Exception as e:
            self.logger.exception(e)
            raise e
        finally:
            return

    async def _consume_async(self, input_generator: AsyncGenerator, input_schema: Schema, log_history: History = None) -> AsyncGenerator:
        if log_history is None:
            log_history = History(schema=input_schema)
        try:
            async for observation in input_generator:
                yield self._consume_observation(observation, log_history, log_history)
        except Exception as e:
            self.logger.exception(e)
            raise e
        finally:
            return
