from __future__ import annotations

import typing

from freedom.domain.valueobject import ValueObject

if typing.TYPE_CHECKING:
    from freedom.domain import event_handler as handler_

EventType = typing.Type["Event"]


class Event(ValueObject):
    pass


class ExceptionEvent(Event):
    __slots__: typing.Sequence[str] = (
        "exception",
        "failed_event",
        "failed_callback",
    )

    def __init__(
        self,
        exception: BaseException,
        failed_event: Event,
        failed_callback: handler_.AnyEventHandler,
    ) -> None:
        self.exception = exception
        self.failed_event = failed_event
        self.failed_callback = failed_callback

    async def retry(self) -> None:
        await self.failed_callback.handle(self.failed_event)
