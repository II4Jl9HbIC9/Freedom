from __future__ import annotations

import inspect
import types
import typing

from freedom import util
from freedom.application import inflector

_AnyHandlerT = typing.TypeVar("_AnyHandlerT")
_TargetHandlerT = typing.TypeVar("_TargetHandlerT", bound=typing.Type[typing.Any])
_TargetT = typing.TypeVar("_TargetT", bound=typing.Type[typing.Any])


class InMemoryInflector(inflector.Inflector[_TargetT, _TargetHandlerT]):
    __slots__ = (
        "_handlers",
        "_handler_type",
    )

    def __init__(
        self,
        *,
        handler_type: _TargetHandlerT,  # To get args from generic[]
        handlers: typing.Optional[
            inflector.TargetHandlersType[_TargetT, _TargetHandlerT]
        ] = None,
    ) -> None:
        if handlers is None:
            handlers = {}

        self._handlers = handlers
        self._handler_type = handler_type

    def listen(
        self,
        handler: typing.Optional[_AnyHandlerT] = None,
        target: typing.Optional[_TargetT] = None,
    ) -> typing.Union[_AnyHandlerT, typing.Callable[[_AnyHandlerT], _AnyHandlerT]]:
        def wrap(target_handler: _AnyHandlerT) -> _AnyHandlerT:
            if not inspect.isclass(target_handler):
                raise ValueError(f"Handler class expected, got {target_handler!r}")

            target_ref = target  # Avoid unresolved reference 'command'
            if target_ref is None:
                target_ref = typing.cast(
                    _TargetT,
                    util.get_base_args(
                        handler,
                        base_type=self._handler_type,
                    )[0],
                )
            assert target_ref is not None

            self.subscribe(typing.cast(_TargetHandlerT, target_handler), target_ref)
            return typing.cast(_AnyHandlerT, target_handler)

        if handler is None:
            return wrap

        return wrap(handler)

    def get_handler_for(self, target: _TargetT) -> typing.Optional[_TargetHandlerT]:
        return typing.cast(
            typing.Optional[_TargetHandlerT], self._handlers.get(target, None)
        )

    def get_handlers(
        self,
    ) -> inflector.TargetHandlersViewType[_TargetT, _TargetHandlerT]:
        return types.MappingProxyType(self._handlers)

    def subscribe(
        self,
        handler: _TargetHandlerT,
        target: _TargetT,
        allow_many: bool = False,
    ) -> None:
        if not allow_many and target in self._handlers:
            raise ValueError(f"Target {target!r} is already subscribed")
        self._handlers[target] = handler

    def unsubscribe(
        self, target: _TargetT, handler: typing.Optional[_TargetHandlerT] = None
    ) -> None:
        if target not in self._handlers:
            raise ValueError(f"Command {target!r} is not subscribed")

        if handler is not None:
            if isinstance(handler, typing.Iterable):
                handlers = typing.cast(
                    typing.List[_TargetHandlerT],
                    self.get_handler_for(target) or [],
                )
                for h in handler:
                    handlers.remove(h)

                self._handlers[target] = handlers
            else:
                handlers = typing.cast(
                    typing.List[_TargetHandlerT],
                    self.get_handler_for(target) or [],
                )
                for h in handlers:
                    if h is handler:
                        handlers.remove(h)

                self._handlers[target] = handlers

            return

        self._handlers.pop(target)
