from __future__ import annotations

__all__: typing.Sequence[str] = ("CommandBus",)

import abc
import typing

if typing.TYPE_CHECKING:
    from freedom.application import inflector as inflector_
    from freedom.domain import command as command_
    from freedom.domain import command_handler as handler_


class CommandBus(abc.ABC):
    __slots__: typing.Sequence[str] = ()

    @abc.abstractmethod
    async def execute(self, command: command_.Command) -> handler_.CommandResult: ...

    @abc.abstractmethod
    @typing.overload
    def listen(
        self,
        handler: typing.Literal[None],
        command: typing.Optional[command_.CommandType] = None,
    ) -> typing.Callable[
        [handler_.AnyCommandHandlerTypeT], handler_.AnyCommandHandlerTypeT
    ]: ...

    @abc.abstractmethod
    @typing.overload
    def listen(
        self,
        handler: handler_.AnyCommandHandlerTypeT,
        command: typing.Optional[command_.CommandType] = None,
    ) -> handler_.AnyCommandHandlerTypeT: ...

    @abc.abstractmethod
    def listen(
        self,
        handler: typing.Optional[handler_.AnyCommandHandlerTypeT] = None,
        command: typing.Optional[command_.CommandType] = None,
    ) -> typing.Union[
        handler_.AnyCommandHandlerTypeT,
        typing.Callable[
            [handler_.AnyCommandHandlerTypeT],
            handler_.AnyCommandHandlerTypeT,
        ],
    ]: ...

    @abc.abstractmethod
    def get_handler_for(
        self,
        command: command_.CommandType,
    ) -> typing.Optional[handler_.AnyCommandHandlerType]: ...

    @abc.abstractmethod
    def get_handlers(self) -> inflector_.TargetHandlersViewType[
        command_.CommandType,
        handler_.AnyCommandHandlerType,
    ]: ...

    @abc.abstractmethod
    def subscribe(
        self,
        handler: handler_.AnyCommandHandlerType,
        command: command_.CommandType,
    ) -> None: ...

    @abc.abstractmethod
    def unsubscribe(self, command: command_.CommandType) -> None: ...
