from __future__ import annotations

__all__: typing.Sequence[str] = (
    "EventHandler",
    "AnyEventHandlerTypeT",
    "AnyEventHandlerType",
)

import abc
import typing

import typing_extensions as typingext

AnyEventHandler: typingext.TypeAlias = "EventHandler[typing.Any]"
AnyEventHandlerType: typingext.TypeAlias = typing.Type[AnyEventHandler]
AnyEventHandlerTypeT = typing.TypeVar("AnyEventHandlerTypeT", bound=AnyEventHandlerType)

_EventT = typing.TypeVar("_EventT")


class EventHandler(abc.ABC, typing.Generic[_EventT]):
    __slots__: typing.Sequence[str] = ()

    if typing.TYPE_CHECKING:

        def __call__(self, *args: typing.Any, **kwargs: typing.Any) -> typing.Any: ...

    @abc.abstractmethod
    async def handle(self, event: _EventT, /) -> None: ...
