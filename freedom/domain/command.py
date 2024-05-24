from __future__ import annotations

__all__: typing.Sequence[str] = ("Command", "CommandType")

import typing

from src.domain.valueobject import ValueObject

CommandType = typing.Type["Command"]


class Command(ValueObject):
    __slots__: typing.Sequence[str] = ()
