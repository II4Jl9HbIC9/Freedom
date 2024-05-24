from __future__ import annotations

__all__: typing.Sequence[str] = ("Repository",)

import abc
import typing

import typing_extensions as typingext

if typing.TYPE_CHECKING:
    from freedom.domain import event

_AggregateRootIdT = typing.TypeVar("_AggregateRootIdT")
_AggregateRootT = typing.TypeVar("_AggregateRootT")

AnyRepository: typingext.TypeAlias = "Repository[typing.Any, typing.Any]"


class Repository(abc.ABC, typing.Generic[_AggregateRootIdT, _AggregateRootT]):
    __slots__: typing.Sequence[str] = ()

    @abc.abstractmethod
    async def get_by_id(
        self, aggregate_id: _AggregateRootIdT
    ) -> typing.Optional[_AggregateRootT]: ...

    @abc.abstractmethod
    async def remove_by_id(self, aggregate_id: _AggregateRootIdT) -> None: ...

    @abc.abstractmethod
    async def remove(self, aggregate: _AggregateRootT) -> None: ...

    @abc.abstractmethod
    async def insert(self, aggregate: _AggregateRootT) -> None: ...

    @abc.abstractmethod
    async def save(self, aggregate: _AggregateRootT) -> None: ...

    @abc.abstractmethod
    async def persist(self, aggregate: _AggregateRootT) -> None: ...

    @abc.abstractmethod
    async def persist_all(self) -> None: ...

    @abc.abstractmethod
    def collect_events(self) -> typing.List[event.Event]: ...
