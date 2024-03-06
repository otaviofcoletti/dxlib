from __future__ import annotations

import enum
from typing import List

import pandas as pd

from ..security import SecurityManager, Security
from ...trading import Signal


class SchemaLevel(enum.Enum):
    DATE = "date"
    SECURITY = "security"

    def to_dict(self):
        return {
            "value": self.value
        }

    @classmethod
    def from_dict(cls, **kwargs):
        return cls(kwargs["value"].lower())


class Schema:
    levels: List[SchemaLevel]
    fields: List[str]
    security_manager: SecurityManager

    def __repr__(self):
        return f"Schema(levels={self.levels}, fields={self.fields}, security_manager={self.security_manager})"

    def __str__(self):
        return f"Schema(levels={self.levels}, fields={self.fields}, security_manager={self.security_manager})"

    def __init__(
            self,
            levels: List[SchemaLevel] = None,
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
        if not kwargs:
            return cls()
        return cls(
            levels=[SchemaLevel.from_dict(**level) for level in kwargs["levels"]],
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

        if SchemaLevel.SECURITY in self.levels:
            security_level = df.index.names.index(SchemaLevel.SECURITY.value)

            df.index = df.index.set_levels(
                df.index.levels[security_level].map(
                    lambda x: self.security_manager.add(Security.from_dict(**self.deserialize(x)))
                ),
                level=SchemaLevel.SECURITY.value
            )
        if "signal" in self.fields:
            df["signal"] = df["signal"].map(
                lambda kwargs: Signal.from_dict(**self.deserialize(kwargs))
            )

        return df
