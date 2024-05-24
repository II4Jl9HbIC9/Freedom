from __future__ import annotations

import abc
import types
import typing

import typing_extensions as typingext

_TargetHandlerT = typing.TypeVar("_TargetHandlerT")
_TargetT = typing.TypeVar("_TargetT")

TargetHandlersType: typingext.TypeAlias = (
    typing.MutableMapping
)  # [_TargetT, _TargetHandlerT]
TargetHandlersViewType: typingext.TypeAlias = (
    types.MappingProxyType
)  # [_TargetT, _TargetHandlerT]

_AnyHandlerT = typing.TypeVar("_AnyHandlerT")


class Inflector(abc.ABC, typing.Generic[_TargetT, _TargetHandlerT]):
    __slots__: typing.Sequence[str] = ()

    # @abc.abstractmethod
    # @typing.overload
    # def listen(
    #     self,
    #     handler: typing.Literal[None],
    #     target: typing.Optional[_TargetT] = None,
    # ) -> typing.Callable[[_TargetHandlerT], _TargetHandlerT]: ...
    #
    # @abc.abstractmethod
    # @typing.overload
    # def listen(
    #     self,
    #     handler: _TargetHandlerT,
    #     target: typing.Optional[_TargetT] = None,
    # ) -> _TargetHandlerT: ...

    @abc.abstractmethod
    def listen(
        self,
        handler: typing.Optional[_AnyHandlerT] = None,
        target: typing.Optional[_TargetT] = None,
    ) -> typing.Union[_AnyHandlerT, typing.Callable[[_AnyHandlerT], _AnyHandlerT]]: ...

    @abc.abstractmethod
    def get_handler_for(self, target: _TargetT) -> typing.Optional[_TargetHandlerT]: ...

    @abc.abstractmethod
    def get_handlers(self) -> TargetHandlersViewType[_TargetT, _TargetHandlerT]: ...

    @abc.abstractmethod
    def subscribe(
        self,
        handler: _TargetHandlerT,
        target: _TargetT,
        allow_many: bool = False,
    ) -> None: ...

    @abc.abstractmethod
    def unsubscribe(
        self,
        target: _TargetT,
        handler: typing.Optional[_TargetHandlerT] = None,
    ) -> None: ...
