from __future__ import annotations

__all__: typing.Sequence[str] = ("Uuid4EntityId",)

import typing
import uuid

from freedom.domain import entity_id


class Uuid4EntityId(entity_id.EntityId):
    __slots__: typing.Sequence[str] = ()

    @classmethod
    def next_id(cls) -> Uuid4EntityId:
        self = cls(int=uuid.uuid4().int)
        return self
