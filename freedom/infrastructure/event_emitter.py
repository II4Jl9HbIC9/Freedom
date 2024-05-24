from __future__ import annotations

__all__: typing.Sequence[str] = ("InMemoryEventEmitter",)

import asyncio
import collections
import inspect
import typing

from freedom import util
from freedom.application import event_emitter
from freedom.application import inflector as inflector_
from freedom.application import provider as provider_
from freedom.domain import event as event_
from freedom.domain import event_handler as handler_
from freedom.infrastructure import inflector as inflector_impl


class InMemoryEventEmitter(event_emitter.EventEmitter):
    __slots__: typing.Sequence[str] = (
        "_waiters",
        "_inflector",
        "_provider",
        "_dispatch_on_exc",
    )

    def __init__(
        self,
        *,
        provider: typing.Optional[provider_.AnyDependencyProviderType] = None,
        inflector: typing.Optional[
            inflector_.Inflector[
                event_.EventType,
                typing.List[handler_.AnyEventHandlerType],
            ]
        ] = None,
        dispatch_on_exc: bool = True,
    ) -> None:
        if inflector is None:
            inflector = typing.cast(
                inflector_.Inflector[
                    event_.EventType,
                    typing.List[handler_.AnyEventHandlerType],
                ],
                inflector_impl.InMemoryInflector(
                    handler_type=handler_.EventHandler,
                ),
            )

        self._dispatch_on_exc = dispatch_on_exc
        self._waiters: typing.Any = collections.defaultdict(set)  # FIXME
        self._inflector = inflector
        self._provider = provider

    def emit(self, event: event_.Event, /) -> asyncio.Future[typing.Any]:
        event_type = type(event)
        tasks: typing.List[typing.Coroutine[None, typing.Any, None]] = []

        handlers = self.get_handler_for(event_type)
        if handlers:
            for handler in handlers:
                if inspect.isclass(handler):
                    dependencies: typing.Dict[str, typing.Any] = {}
                    if self._provider is not None:
                        dependencies.update(
                            self._provider.get_dependencies(handler.__init__)
                        )

                    handler = handler(**dependencies)

                tasks.append(self._trigger_handler(handler, event))

        waiter_set = self._waiters[event_type]

        for waiter in tuple(waiter_set):
            predicate, future = waiter
            if not future.done():
                try:
                    if predicate and not predicate(event):
                        continue
                except Exception as exc:
                    future.set_exception(exc)
                else:
                    future.set_result(event)

            waiter_set.remove(waiter)

        if tasks:
            return asyncio.gather(*tasks)

        return util.as_completed_future()

    def listen(
        self,
        handler: typing.Optional[handler_.AnyEventHandlerType] = None,
        event: typing.Optional[event_.EventType] = None,
    ) -> typing.Union[
        handler_.AnyEventHandlerType,
        typing.Callable[
            [handler_.AnyEventHandlerType],
            handler_.AnyEventHandlerType,
        ],
    ]:
        return self._inflector.listen(handler, event)

    def get_handler_for(
        self,
        event: event_.EventType,
    ) -> typing.Optional[typing.List[handler_.AnyEventHandlerType]]:
        return self._inflector.get_handler_for(event)

    def get_handlers(self) -> inflector_.TargetHandlersViewType[
        event_.EventType,
        typing.List[handler_.AnyEventHandlerType],
    ]:
        return self._inflector.get_handlers()

    def subscribe(
        self,
        handler: handler_.AnyEventHandlerType,
        event: event_.EventType,
    ) -> None:
        handlers = self.get_handler_for(event)
        if handlers is None:
            handlers = []

        handlers.append(handler)
        self._inflector.subscribe(handlers, event, allow_many=True)

    def unsubscribe(
        self, handler: handler_.AnyEventHandlerType, event: event_.EventType
    ) -> None:
        self._inflector.unsubscribe(event, handler)

    async def wait_for(
        self,
        event_type: event_.EventType,
        /,
        timeout: typing.Union[float, int, None],
        predicate: typing.Optional[typing.Callable[[typing.Any], bool]] = None,
    ) -> event_.Event:
        future = util.get_loop().create_future()

        if predicate is None:
            predicate = lambda _: True

        waiter_set = self._waiters[event_type]
        item = (predicate, future)
        waiter_set.add(item)

        try:
            event = await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            waiter_set.remove(item)
            raise

        return typing.cast(event_.Event, event)

    async def _trigger_handler(
        self,
        callback: typing.Callable[..., typing.Awaitable[None]],
        event: event_.Event,
    ) -> None:
        try:
            if isinstance(callback, handler_.EventHandler):
                await callback.handle(event)
                return
            await callback(event)
        except Exception as exc:
            if not self._dispatch_on_exc:
                raise exc

            exc_event = event_.ExceptionEvent(
                exception=exc,
                failed_event=event,
                failed_callback=callback,
            )
            await self.emit(exc_event)
