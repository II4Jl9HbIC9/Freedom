from __future__ import annotations

import inspect
import typing

from freedom import sentinel
from freedom.application import provider


class InMemoryDependencyProvider(
    provider.DependencyProvider[typing.Type[typing.Any], typing.Any]
):
    __slots__: typing.Sequence[str] = ("_dependencies",)

    def __init__(
        self,
        overrides: typing.Optional[
            typing.Mapping[typing.Type[typing.Any], typing.Any]
        ] = None,
    ) -> None:
        self._dependencies: typing.Dict[typing.Type[typing.Any], typing.Any] = {}

        if overrides is not None:
            for k, v in overrides.items():
                self.register_dependency(k, v)

    def register_dependency(
        self,
        identifier: typing.Type[typing.Any],
        dependency: typing.Any,
    ) -> None:
        if not inspect.isclass(identifier):
            raise ValueError("Dependency identifier must be a type.")
        self._dependencies[identifier] = dependency

    def get_dependency(self, identifier: typing.Type[typing.Any]) -> typing.Any:
        dependency = self._dependencies.get(identifier, sentinel.NOTHING)
        if dependency is sentinel.NOTHING:
            raise ValueError(f"No dependency found with identifier {identifier!r}.")
        return dependency
