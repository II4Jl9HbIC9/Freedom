from __future__ import annotations

import asyncio
import types
import typing
import weakref

import typing_extensions as typingext

from freedom.domain import event as event_

if typing.TYPE_CHECKING:
    from freedom.application import event_emitter as emitter_


def _generate_weak_listener(
    reference: weakref.WeakMethod[typing.Any],
) -> typing.Callable[[event_.Event], typing.Coroutine[typing.Any, typing.Any, None]]:
    async def call_weak_method(event: event_.Event) -> None:
        method = reference()
        if method is None:
            raise TypeError(
                "dead weak referenced subscriber method cannot be executed, "
                "try actually closing your event streamers"
            )

        await method(event)

    return call_weak_method


class EventStream:
    __slots__: typing.Sequence[str] = (
        "__weakref__",
        "_active",
        "_event",
        "_event_manager",
        "_event_type",
        "_filters",
        "_limit",
        "_queue",
        "_registered_listener",
        "_timeout",
    )

    __weakref__: typing.Optional[weakref.ref[EventStream]]

    def __init__(
        self,
        emitter: emitter_.EventEmitter,
        event_type: typing.Type[event_.Event],
        *,
        timeout: typing.Union[float, int, None],
        limit: typing.Optional[int] = None,
    ) -> None:
        self._active = False
        self._event: typing.Optional[asyncio.Event] = None
        self._event_manager = emitter
        self._event_type = event_type
        self._limit = limit
        self._queue: typing.List[event_.Event] = []
        self._registered_listener: typing.Optional[
            typing.Callable[
                [event_.Event], typing.Coroutine[typing.Any, typing.Any, None]
            ]
        ] = None
        self._timeout = timeout

    def __enter__(self) -> typingext.Self:
        self.open()
        return self

    def __exit__(
        self,
        exc_type: typing.Optional[typing.Type[BaseException]],
        exc_val: typing.Optional[BaseException],
        exc_tb: typing.Optional[types.TracebackType],
    ) -> None:
        self.close()

    def __aiter__(self) -> typing.AsyncIterator[event_.Event]:
        return self

    async def __anext__(self) -> event_.Event:
        if not self._active:
            raise TypeError("stream must be started with before entering it")

        while not self._queue:
            if not self._event:
                self._event = asyncio.Event()

            try:
                await asyncio.wait_for(self._event.wait(), timeout=self._timeout)
            except asyncio.TimeoutError:
                raise StopAsyncIteration from None

            self._event.clear()

        return self._queue.pop(0)

    def __await__(self) -> typing.Generator[None, None, typing.Sequence[event_.Event]]:
        async def _await_all() -> typing.Sequence[event_.Event]:
            self.open()
            result = [
                event
                async for event in typing.cast(typing.AsyncIterable[event_.Event], self)
            ]
            self.close()
            return result

        return _await_all().__await__()

    def __del__(self) -> None:
        if self._active:
            # _LOGGER.warning(
            # "active %r streamer fell out of scope before being closed",
            # self._event_type.__name__)
            self.close()

    async def _listener(self, event: event_.Event) -> None:
        if self._limit is not None and len(self._queue) >= self._limit:
            return

        self._queue.append(event)
        if self._event:
            self._event.set()

    def close(self) -> None:
        if self._active and self._registered_listener is not None:
            try:
                self._event_manager.unsubscribe(
                    self._registered_listener, self._event_type
                )
            except ValueError as exc:
                # FIXME
                pass

            self._registered_listener = None

        self._active = False

    def filter(
        self, condition: typing.Callable[[event_.Event], bool]
    ) -> typingext.Self:
        if self._active:
            self._queue = [entry for entry in self._queue if condition(entry)]

        return self

    def open(self) -> None:
        if not self._active:
            reference = weakref.WeakMethod(self._listener)
            listener = _generate_weak_listener(reference)

            self._registered_listener = listener
            self._event_manager.subscribe(listener, self._event_type)
            self._active = True
