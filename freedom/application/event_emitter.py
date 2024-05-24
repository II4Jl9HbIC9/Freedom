from __future__ import annotations

__all__: typing.Sequence[str] = ("EventEmitter",)

import abc
import asyncio
import typing

if typing.TYPE_CHECKING:
    from freedom.application import inflector
    from freedom.domain import event as event_
    from freedom.domain import event_handler as handler_


class EventEmitter(abc.ABC):
    __slots__: typing.Sequence[str] = ()

    @abc.abstractmethod
    def emit(self, event: event_.Event, /) -> asyncio.Future[typing.Any]: ...

    @abc.abstractmethod
    def listen(
        self,
        handler: typing.Optional[handler_.AnyEventHandlerTypeT] = None,
        event: typing.Optional[event_.EventType] = None,
    ) -> typing.Union[
        handler_.AnyEventHandlerTypeT,
        typing.Callable[
            [handler_.AnyEventHandlerTypeT],
            handler_.AnyEventHandlerTypeT,
        ],
    ]: ...

    @abc.abstractmethod
    def get_handler_for(
        self,
        event: event_.EventType,
    ) -> typing.Optional[handler_.AnyEventHandlerType]: ...

    @abc.abstractmethod
    def get_handlers(self) -> inflector.TargetHandlersViewType[
        event_.EventType,
        handler_.AnyEventHandlerType,
    ]: ...

    @abc.abstractmethod
    def subscribe(
        self,
        handler: handler_.AnyEventHandlerType,
        event: event_.EventType,
    ) -> None: ...

    @abc.abstractmethod
    def unsubscribe(
        self, handler: handler_.AnyEventHandlerType, event: event_.EventType
    ) -> None: ...

    @abc.abstractmethod
    async def wait_for(
        self,
        event_type: event_.EventType,
        /,
        timeout: typing.Union[float, int, None],
        predicate: typing.Optional[typing.Callable[[event_.EventType], bool]] = None,
    ) -> event_.Event: ...

    # @abc.abstractmethod
    # def attach_stream(self, stream):
    #     pass
