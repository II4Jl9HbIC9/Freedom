from __future__ import annotations

import abc
import typing
import uuid

from freedom.domain.valueobject import ValueObject


class EntityId(ValueObject, abc.ABC):
    __slots__: typing.Sequence[str] = ()

    def __init__(self, int: int) -> None:
        self._int = int

    @classmethod
    @abc.abstractmethod
    def next_id(cls, **kwargs: typing.Any) -> EntityId: ...

    @property
    def int(self) -> int:
        return self._int

    @property
    def str(self) -> str:
        return str(self.int)


class EntityIdUuid4(EntityId):
    @classmethod
    def next_id(cls, **kwargs: typing.Any) -> EntityIdUuid4:
        return cls(int=uuid.uuid4().int)


class EntityIdSequential(EntityId):
    @classmethod
    def next_id(cls, **kwargs: typing.Any) -> EntityIdSequential:
        next_id = kwargs.pop("next_id")
        if not isinstance(next_id, int):
            next_id = int(next_id)
        return cls(int=next_id)
