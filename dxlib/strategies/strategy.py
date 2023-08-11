from abc import ABC

from .. import Signal


class Strategy(ABC):
    def __init__(self):
        pass

    def execute(self, row, idx, history) -> list[Signal]:
        pass
