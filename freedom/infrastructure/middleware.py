from __future__ import annotations

__all__: typing.Sequence[str] = (
    "LoggerMiddleware",
    "MiddlewareChain",
)

import logging
import typing

from freedom import util
from freedom.application import middleware as middleware_


class LoggerMiddleware(middleware_.Middleware):
    __slots__: typing.Sequence[str] = (
        "_logger",
        "_received_level",
        "_succeeded_level",
        "_failed_level",
    )

    def __init__(
        self,
        logger: logging.Logger,
        *,
        received_level: int = logging.DEBUG,
        succeeded_level: int = logging.DEBUG,
        failed_level: int = logging.ERROR,
    ) -> None:
        self._logger = logger
        self._received_level = received_level
        self._succeeded_level = succeeded_level
        self._failed_level = failed_level

    async def __call__(
        self,
        message: typing.Any,
        next_middleware: middleware_.PartialMiddlewareSigType,
    ) -> typing.Any:
        message_type = type(message)

        self._logger.log(
            self._received_level,
            f"Message received: ${message_type}",
        )

        try:
            result = await next_middleware(message)
        except Exception as exc:
            self._logger.log(
                self._failed_level,
                f"Message failed: ${message_type}",
                exc_info=True,
            )
            raise exc

        self._logger.log(
            self._succeeded_level,
            f"Message succeeded: ${message_type}",
        )
        return result


class MiddlewareChain(middleware_.MiddlewareChain):
    def __init__(
        self,
        executor_middleware: middleware_.MiddlewareSigType,
        middlewares: typing.Optional[typing.List[middleware_.MiddlewareSigType]] = None,
    ) -> None:
        self.middlewares = middlewares or []
        self.executor_middleware = executor_middleware

    async def __call__(self, message: typing.Any) -> typing.Any:
        all_middlewares = (self.middlewares or []) + [self.executor_middleware]

        chain = typing.cast(middleware_.MiddlewareSigType, util.empty_coro)
        for middleware in reversed(all_middlewares):
            chain = self.set_next(middleware, chain)

        result = await chain(message)
        return result

    def set_next(
        self,
        middleware: middleware_.MiddlewareSigType,
        next_middleware: middleware_.MiddlewareSigType,
    ) -> middleware_.PartialMiddlewareSigType:
        async def wrap(message: typing.Any) -> typing.Any:
            result = await middleware(message, next_middleware)
            return result

        return wrap
