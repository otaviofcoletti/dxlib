from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import List

import pandas as pd

from ..security import SecurityManager, Security
from ...trading import Signal, OrderData


class LevelEnum(enum.Enum):
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


class Schema:
    levels: List[LevelEnum]
    fields: List[str]
    security_manager: SecurityManager

    def __init__(
            self,
            levels: List[LevelEnum] = None,
            fields: List[str] = None,
            security_manager: SecurityManager = None,
    ):
        self.levels = levels if levels else []
        self.fields = fields if fields else []
        self.security_manager = (
            security_manager if security_manager else SecurityManager()
        )

    def __add__(self, other: Schema) -> Schema:
        return Schema(
            levels=self.levels + other.levels,
            fields=self.fields + other.fields,
            security_manager=self.security_manager + other.security_manager,
        )

    def __iadd__(self, other: Schema) -> Schema:
        self.extend(other)
        return self

    def extend(self, other: Schema) -> Schema:
        self.levels += other.levels
        self.fields += other.fields
        self.security_manager += other.security_manager
        return self

    def to_dict(self) -> dict:
        return {
            "levels": [level.to_dict() for level in self.levels],
            "fields": self.fields,
            "security_manager": self.security_manager.to_dict(),
        }

    @classmethod
    def from_dict(cls, **kwargs) -> Schema:
        return cls(
            levels=[LevelEnum.from_dict(**level) for level in kwargs["levels"]],
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

        return df


class StandardLevel(LevelEnum):
    DATE = "date"
    SECURITY = "security"


@dataclass
class StandardSchema(Schema):
    levels: List[StandardLevel]
    fields: List[str]
    security_manager: SecurityManager

    def __init__(
            self,
            levels: List[StandardLevel] = None,
            fields: List[str] = None,
            security_manager: SecurityManager = None,
    ):
        super().__init__(levels, fields, security_manager)

    @classmethod
    def from_dict(cls, **kwargs) -> StandardSchema:
        return cls(
            levels=[StandardLevel.from_dict(**level) for level in kwargs["levels"]],
            fields=kwargs["fields"],
            security_manager=SecurityManager.from_dict(
                **kwargs.get("security_manager")
            ),
        )

    @classmethod
    def serialize(cls, obj: any):
        obj = super().serialize(obj)
        if isinstance(obj, Security):
            return cls.serialize(obj.to_dict())
        return obj

    def apply_deserialize(self, df: pd.DataFrame):
        # Converts a pd.DataFrame into this schema's format
        # For example, if pd.DataFrame's index is a string of a tuple of date and security
        # Make the new index a multiindex with date and security objects
        df = super().apply_deserialize(df)
        if StandardLevel.SECURITY in self.levels:
            security_level = df.index.names.index(StandardLevel.SECURITY.value)

            df.index = df.index.set_levels(
                df.index.levels[security_level].map(
                    lambda x: self.security_manager.add(Security.from_dict(**self.deserialize(x)))
                ),
                level=StandardLevel.SECURITY.value
            )

        return df


class SignalSchema(Schema):
    def __init__(
            self,
            levels: List[LevelEnum] = None,
            fields: List[str] = None,
            security_manager: SecurityManager = None
    ):
        if fields is None:
            fields = ["signal"]
        super().__init__(levels, fields, security_manager)

    @classmethod
    def serialize(cls, obj: any):
        obj = super().serialize(obj)
        if isinstance(obj, Signal):
            return cls.serialize(obj.to_dict())
        elif isinstance(obj, (Security, Signal)):
            return cls.serialize(obj.to_dict())
        return obj

    def apply_deserialize(self, df: pd.DataFrame):
        df = super().apply_deserialize(df)

        if "signal" in self.fields:
            df["signal"] = df["signal"].map(lambda kwargs: Signal.from_dict(**self.deserialize(kwargs)))

        return df

    @staticmethod
    def to_order_data(df: pd.DataFrame):
        signal_column = "signal"
        security_index = df.index.names.index(StandardLevel.SECURITY.value)
        return df.apply(lambda row: OrderData.from_signal(row[signal_column], row.name[security_index]), axis=1)
