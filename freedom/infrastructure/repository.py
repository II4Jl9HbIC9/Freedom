from __future__ import annotations

__all__: typing.Sequence[str] = ("InMemoryRepository",)

import typing

from freedom.domain import aggregate as aggregate_
from freedom.domain import entity_id
from freedom.domain import event
from freedom.domain import repository

_AggregateRootIdT = typing.TypeVar("_AggregateRootIdT")
_AggregateRootT = typing.TypeVar("_AggregateRootT", bound=aggregate_.AnyAggregateRoot)


class InMemoryRepository(repository.Repository[_AggregateRootIdT, _AggregateRootT]):
    __slots__: typing.Sequence[str] = ("_objects",)

    def __init__(self) -> None:
        self._objects: typing.Dict[entity_id.EntityId, _AggregateRootT] = {}

    async def get_by_id(
        self, aggregate_id: _AggregateRootIdT
    ) -> typing.Optional[_AggregateRootT]:
        try:
            aggregate = self._objects[aggregate_id]
        except KeyError as exc:
            raise KeyError(f"No aggregate found with id {aggregate_id!r}") from exc

        return aggregate

    async def remove_by_id(self, aggregate_id: _AggregateRootIdT) -> None:
        try:
            del self._objects[aggregate_id]
        except KeyError as exc:
            raise KeyError(f"No aggregate found with id {aggregate_id!r}") from exc

    async def remove(self, aggregate: _AggregateRootT) -> None:
        await self.remove_by_id(aggregate.id)

    async def insert(self, aggregate: _AggregateRootT) -> None:
        if aggregate.id in self._objects:
            raise ValueError(f"Aggregate with id {aggregate.id!r} already exists.")

        self._objects[aggregate.id] = aggregate

    async def save(self, aggregate: _AggregateRootT) -> None:
        self._objects[aggregate.id] = aggregate

    persist = save

    async def persist_all(self) -> None:
        return

    def collect_events(self) -> typing.List[event.Event]:
        events = []
        for aggregate in self._objects.values():
            events.extend(aggregate.collect_events())

        return events
