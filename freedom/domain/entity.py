from __future__ import annotations

import typing

from freedom.domain.business_rule import BusinessRuleValidationMixin
from freedom.domain.entity_id import EntityId

_EntityIdT = typing.TypeVar("_EntityIdT", bound=EntityId)


class Entity(BusinessRuleValidationMixin, typing.Generic[_EntityIdT]):
    __slots__: typing.Sequence[str] = ("_id",)

    def __init__(self, id: _EntityIdT) -> None:
        self._id = id

    @property
    def id(self) -> _EntityIdT:
        return self._id
