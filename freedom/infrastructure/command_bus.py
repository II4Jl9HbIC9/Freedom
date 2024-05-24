from __future__ import annotations

__all__: typing.Sequence[str] = ("InMemoryCommandBus",)

import typing

from freedom.application import application
from freedom.application import command_bus
from freedom.application import inflector as inflector_
from freedom.domain import command as command_
from freedom.domain import command_handler as handler_
from freedom.infrastructure import inflector as inflector_impl
from freedom.infrastructure import middleware as middleware_impl

if typing.TYPE_CHECKING:
    from freedom.application import middleware
    from freedom.application import provider as provider_


class InMemoryCommandBus(command_bus.CommandBus):
    __slots__: typing.Sequence[str] = (
        "_handlers",
        "_provider",
        "_inflector",
        "_middlewares_chain",
    )

    def __init__(
        self,
        middlewares: typing.Optional[typing.List[middleware.MiddlewareSigType]] = None,
        provider: typing.Optional[provider_.AnyDependencyProviderType] = None,
        inflector: typing.Optional[
            inflector_.Inflector[command_.CommandType, handler_.AnyCommandHandlerType]
        ] = None,
    ) -> None:
        if inflector is None:
            inflector = typing.cast(
                inflector_.Inflector[
                    command_.CommandType,
                    handler_.AnyCommandHandlerType,
                ],
                inflector_impl.InMemoryInflector(
                    handler_type=handler_.CommandHandler,
                ),
            )

        self._middlewares_chain = middleware_impl.MiddlewareChain(
            self._executor_middleware,
            middlewares or [],
        )
        self._inflector = inflector
        self._provider = provider
        self._handlers: inflector_.TargetHandlersType[
            command_.CommandType, handler_.AnyCommandHandlerType
        ] = {}

    @typing.overload
    def listen(
        self,
        handler: typing.Literal[None],
        command: typing.Optional[command_.CommandType] = None,
    ) -> typing.Callable[
        [handler_.AnyCommandHandlerTypeT], handler_.AnyCommandHandlerTypeT
    ]: ...

    @typing.overload
    def listen(
        self,
        handler: handler_.AnyCommandHandlerTypeT,
        command: typing.Optional[command_.CommandType] = None,
    ) -> handler_.AnyCommandHandlerTypeT: ...

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
    ]:
        return self._inflector.listen(handler, command)

    def get_handler_for(
        self, command: command_.CommandType
    ) -> typing.Optional[handler_.AnyCommandHandlerType]:
        return self._inflector.get_handler_for(command)

    def get_handlers(
        self,
    ) -> inflector_.TargetHandlersViewType[
        command_.CommandType, handler_.AnyCommandHandlerType
    ]:
        return self._inflector.get_handlers()

    def subscribe(
        self,
        handler: handler_.AnyCommandHandlerType,
        command: command_.CommandType,
    ) -> None:
        self._inflector.subscribe(handler, command)

    def unsubscribe(self, command: command_.CommandType) -> None:
        self._inflector.unsubscribe(command)

    async def execute(self, command: command_.Command) -> handler_.CommandResult:
        result = typing.cast(
            handler_.CommandResult,
            await self._middlewares_chain(command),
        )
        return result

    @typing.no_type_check
    async def _executor_middleware(
        self,
        command: command_.Command,
        _: middleware.MiddlewareSigType,
    ) -> handler_.CommandResult:
        command_type = type(command)
        handler = self.get_handler_for(command_type)
        if handler is not None:
            kwargs: typing.Dict[str, typing.Any] = {}

            if self._provider is not None:
                kwargs.update(self._provider.get_dependencies(handler.__init__))

            handler = handler(**kwargs)
            result = typing.cast(
                handler_.CommandResult,
                application.collect_domain_events(
                    await handler.handle(command),
                    kwargs,
                ),
            )
            return result

        return handler_.CommandResult.failure(
            fail_message="Handler not found.",
        )
