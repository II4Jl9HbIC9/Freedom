from __future__ import annotations

__all__: typing.Sequence[str] = (
    "AnyCommandHandlerTypeT",
    "CommandHandler",
    "CommandResultError",
    "CommandResult",
)

import abc
import sys
import typing

import typing_extensions as typingext

from freedom.domain.command import Command

if typing.TYPE_CHECKING:
    from freedom import type_hints
    from freedom.domain import entity_id as entity_id_
    from freedom.domain import event as event_

AnyCommandHandler: typingext.TypeAlias = "CommandHandler[typing.Any]"
AnyCommandHandlerType: typingext.TypeAlias = typing.Type[AnyCommandHandler]
AnyCommandHandlerTypeT = typing.TypeVar(
    "AnyCommandHandlerTypeT", bound=AnyCommandHandlerType
)

_CommandT = typing.TypeVar("_CommandT", bound=Command)


class CommandHandler(abc.ABC, typing.Generic[_CommandT]):
    __slots__: typing.Sequence[str] = ()

    if typing.TYPE_CHECKING:

        def __call__(self, *args: typing.Any, **kwargs: typing.Any) -> typing.Any: ...

    @abc.abstractmethod
    async def handle(self, command: _CommandT, /) -> CommandResult: ...


class CommandResultError:
    __slots__: typing.Sequence[str] = (
        "message",
        "exception",
        "exception_info",
    )

    def __init__(
        self,
        message: str,
        exception: typing.Optional[BaseException] = None,
        exception_info: typing.Optional[type_hints.OptionalSysExcInfo] = None,
    ) -> None:
        self.message = message
        self.exception = exception
        self.exception_info = exception_info


class CommandResult:
    __slots__: typing.Sequence[str] = (
        "entity_id",
        "events",
        "errors",
    )

    def __init__(
        self,
        entity_id: typing.Optional[entity_id_.EntityId] = None,
        events: typing.List[event_.Event] = None,
        errors: typing.List[CommandResultError] = None,
    ) -> None:
        self.entity_id = entity_id
        self.events = events or []
        self.errors = errors or []

    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def is_success(self) -> bool:
        return not self.has_errors()

    def add_error(self, command_error: CommandResultError, /) -> None:
        self.errors.append(command_error)

    @classmethod
    def failure(
        cls,
        fail_message: str,
        exception: typing.Optional[BaseException] = None,
        exception_info: typing.Optional[type_hints.OptionalSysExcInfo] = None,
    ) -> CommandResult:
        if exception_info is None:
            exception_info = sys.exc_info()

        result_error = CommandResultError(
            message=fail_message,
            exception=exception,
            exception_info=exception_info,
        )
        result = cls()
        result.add_error(result_error)
        return result

    @classmethod
    def success(
        cls,
        entity_id: typing.Optional[entity_id_.EntityId] = None,
        event: typing.Optional[event_.Event] = None,
        events: typing.Optional[typing.Sequence[event_.Event]] = None,
    ) -> CommandResult:
        events = events or []
        if event is not None:
            events.append(event)

        result = cls(
            entity_id=entity_id,
            events=events,
        )
        return result
