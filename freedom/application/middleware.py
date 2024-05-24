from __future__ import annotations

import abc
import typing

import typing_extensions as typingext

MiddlewareSigType: typingext.TypeAlias = typing.Callable[
    [typing.Any, typing.Any], typing.Awaitable[typing.Any]
]
PartialMiddlewareSigType: typingext.TypeAlias = typing.Callable[
    [typing.Any], typing.Awaitable[typing.Any]
]


# TODO: Make middlewares Generic ?


class Middleware(abc.ABC):
    @abc.abstractmethod
    async def __call__(
        self,
        message: typing.Any,
        next_middleware: PartialMiddlewareSigType,
    ) -> typing.Any: ...


class MiddlewareChain(abc.ABC):
    @abc.abstractmethod
    async def __call__(self, message: typing.Any) -> typing.Any: ...

    @abc.abstractmethod
    def set_next(
        self,
        middleware: MiddlewareSigType,
        next_middleware: MiddlewareSigType,
    ) -> PartialMiddlewareSigType: ...
