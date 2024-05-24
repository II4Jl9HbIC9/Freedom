from __future__ import annotations

import abc
import types
import typing

import typing_extensions

from freedom.domain import event as event_

_EventT = typing.TypeVar("_EventT")


class EventStream(typing.Generic[_EventT]):
    __slots__: typing.Sequence[str] = ()

    @abc.abstractmethod
    def __enter__(self) -> typing_extensions.Self: ...

    @typing.overload
    @abc.abstractmethod
    def __exit__(self, exc_type: None, exc_val: None, exc_tb: None) -> None: ...

    @typing.overload
    @abc.abstractmethod
    def __exit__(
        self,
        exc_type: typing.Type[BaseException],
        exc_val: BaseException,
        exc_tb: types.TracebackType,
    ) -> None: ...

    @abc.abstractmethod
    def __exit__(
        self,
        exc_type: typing.Optional[typing.Type[BaseException]],
        exc_val: typing.Optional[BaseException],
        exc_tb: typing.Optional[types.TracebackType],
    ) -> None: ...

    @abc.abstractmethod
    def __aiter__(self) -> typing_extensions.Self: ...

    @abc.abstractmethod
    async def __anext__(self): ...

    @abc.abstractmethod
    def __await__(
        self,
    ) -> typing.Generator[None, None, typing.Sequence[event_.Event]]: ...

    @abc.abstractmethod
    def __del__(self) -> None: ...

    @abc.abstractmethod
    def close(self) -> None: ...

    @abc.abstractmethod
    def filter(
        self, filter_: typing.Callable[[typing.Sequence[event_.Event]], bool], /
    ): ...

    @abc.abstractmethod
    def open(self) -> None: ...
