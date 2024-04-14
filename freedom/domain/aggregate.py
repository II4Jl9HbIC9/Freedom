# -*- coding: utf-8 -*-
# Copyright (c) 2024 II4Jl9HbIC9
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
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
