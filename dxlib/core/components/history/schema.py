from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import List

import pandas as pd

from ..security import SecurityManager, Security
from ...trading import Signal


class HistoryLevel(enum.Enum):
    DATE = "date"
    SECURITY = "security"

    @classmethod
    def levels(cls):
        return list(cls.__members__.values())

    def to_dict(self):
        return {
            "value": self.value
        }

    @classmethod
    def from_dict(cls, **kwargs):
        return cls(kwargs["value"].lower())


@dataclass
class HistorySchema:
    levels: List[HistoryLevel]
    fields: List[str]
    security_manager: SecurityManager

    def __init__(
            self,
            levels: List[HistoryLevel] = None,
            fields: List[str] = None,
            security_manager: SecurityManager = None,
    ):
        # If parent is not None, then also use the parent's levels and fields
        self.levels = levels if levels else HistoryLevel.levels()
        self.fields = fields if fields else []
        self.security_manager = (
            security_manager if security_manager else SecurityManager()
        )

    def extend(self, other: HistorySchema):
        self.levels.extend(other.levels)
        self.fields.extend(other.fields)
        self.security_manager.extend(other.security_manager)

    def to_dict(self) -> dict:
        return {
            "levels": [level.to_dict() for level in self.levels],
            "fields": self.fields,
            "security_manager": self.security_manager.to_dict(),
        }

    @classmethod
    def from_dict(cls, **kwargs) -> HistorySchema:
        return cls(
            levels=[HistoryLevel.from_dict(**level) for level in kwargs["levels"]],
            fields=kwargs["fields"],
            security_manager=SecurityManager.from_dict(
                **kwargs.get("security_manager")
            ),
        )

    @classmethod
    def serialize(cls, obj: any):
        if isinstance(obj, (int, float, str)):
            return obj
        elif isinstance(obj, dict):
            return tuple((cls.serialize(k), cls.serialize(v)) for k, v in obj.items())
        elif isinstance(obj, (Security, Signal)):
            return cls.serialize(obj.to_dict())
        elif isinstance(obj, pd.Timestamp):
            return cls.serialize(obj.isoformat())
        elif isinstance(obj, (list, pd.Series)):
            return list(map(cls.serialize, obj))
        elif isinstance(obj, tuple):
            return tuple(map(cls.serialize, obj))
        return obj

    @classmethod
    def deserialize(cls, obj: any):
        if isinstance(obj, (int, float, str)):
            return obj
        elif isinstance(obj, (list, tuple)):
            # return dict
            return {cls.deserialize(k): cls.deserialize(v) for k, v in obj}
        return obj

    def apply_deserialize(self, df: pd.DataFrame):
        # Converts a pd.DataFrame into this schema's format
        # For example, if pd.DataFrame's index is a string of a tuple of date and security
        # Make the new index a multiindex with date and security objects
        df.index = pd.MultiIndex.from_tuples(df.index, names=[level.value for level in self.levels])

        if HistoryLevel.SECURITY in self.levels:
            security_level = df.index.names.index(HistoryLevel.SECURITY.value)

            df.index = df.index.set_levels(
                df.index.levels[security_level].map(
                    lambda x: self.security_manager.add(Security.from_dict(**self.deserialize(x)))
                ),
                level=HistoryLevel.SECURITY.value
            )

        return df


class SignalSchema(HistorySchema):
    def __init__(
            self,
            levels: List[HistoryLevel] = None,
            fields: List[str] = None,
            security_manager: SecurityManager = None
    ):
        if fields is None:
            fields = ["signal"]
        super().__init__(levels, fields, security_manager)

    def apply_deserialize(self, df: pd.DataFrame):
        df = super().apply_deserialize(df)

        if "signal" in self.fields:
            df["signal"] = df["signal"].map(lambda kwargs: Signal.from_dict(**self.deserialize(kwargs)))

        return df
