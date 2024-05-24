from __future__ import annotations

import abc
import inspect
import typing

import typing_extensions as typingext

from freedom.sentinel import NOTHING
from freedom.util import get_type_hints

_KeyT = typing.TypeVar("_KeyT")
_ValueT = typing.TypeVar("_ValueT")

AnyDependencyProviderType: typingext.TypeAlias = (
    "DependencyProvider[typing.Any, typing.Any]"
)


class DependencyProvider(abc.ABC, typing.Generic[_KeyT, _ValueT]):
    __slots__: typing.Sequence[str] = ()

    @abc.abstractmethod
    def register_dependency(self, identifier: _KeyT, dependency: _ValueT) -> None: ...

    @abc.abstractmethod
    def get_dependency(self, identifier: _KeyT) -> _ValueT: ...

    def _resolve_arguments(
        self,
        callable_hints: typing.Mapping[str, typing.Any],
    ) -> typing.MutableMapping[str, typing.Any]:
        kwargs = {}
        for arg_name, arg_type in callable_hints.items():
            if arg_type is NOTHING:
                raise KeyError(f"No type hints found for param {arg_name!r}.")

            kwargs[arg_name] = self.get_dependency(arg_type)

        return kwargs

    def get_dependencies(
        self,
        callable_: typing.Callable[..., typing.Any],
    ) -> typing.Mapping[str, typing.Any]:
        sig = inspect.Signature.from_callable(callable_)
        hints = typing.get_type_hints(callable_)
        deps = {}

        for param in sig.parameters.values():
            if param.annotation is inspect.Parameter.empty:
                continue
                # raise KeyError(f"No type hints found for param {param.name!r}.")

            deps[param.name] = self.get_dependency(hints[param.name])

        return deps
        # hints = get_type_hints(callable_)
        # print(hints)
        #
        # # FIXME
        # hints.pop("self", None)
        # hints.pop("return", None)
        #
        # for arg_name, arg_type in hints.copy().items():
        #     if arg_type is NOTHING:
        #         raise KeyError(f"No type hints found for param {arg_name!r}.")
        #
        #     hints[arg_name] = self.get_dependency(arg_type)
        #
        # return hints
