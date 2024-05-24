from __future__ import annotations

import typing

import typing_extensions as typingext

from freedom.domain import entity
from freedom.domain import entity_id
from freedom.domain import event as event_

_AggregateIdT = typing.TypeVar("_AggregateIdT", bound=entity_id.EntityId)

AnyAggregateRoot: typingext.TypeAlias = "AggregateRoot[typing.Any]"


class AggregateRoot(entity.Entity[_AggregateIdT]):
    __slots__: typing.Sequence[str] = ("_uncommitted_events",)

    def __init__(self, id: _AggregateIdT) -> None:
        super().__init__(id=id)
        self._uncommitted_events: typing.List[event_.Event] = []

    @property
    def uncommitted_events(self) -> typing.List[event_.Event]:
        return self._uncommitted_events

    def collect_events(self) -> typing.Sequence[event_.Event]:
        events = self._uncommitted_events[:]
        self._uncommitted_events.clear()
        return events

    def record_that(self, event: event_.Event) -> None:
        self._uncommitted_events.append(event)
