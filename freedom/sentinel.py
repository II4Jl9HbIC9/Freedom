from __future__ import annotations

__all__: typing.Sequence[str] = (
    "NOTHING",
    "NothingOr",
)

import typing

import typing_extensions

_SelfT = typing.TypeVar("_SelfT")


def __new__(_: typing.Type[_SelfT]) -> _SelfT:
    raise TypeError(f"Cannot create multiple instances of NothingType.")


class NothingType:
    __slots__: typing.Sequence[str] = ()

    def __str__(self) -> str:
        return "NOTHING"

    def __repr__(self) -> str:
        return "NOTHING"

    def __reduce__(self) -> str:
        return "NOTHING"

    def __getstate__(self) -> typing.Any:
        return False

    def __bool__(self) -> typing.Literal[False]:
        return False

    def __copy__(self) -> typing_extensions.Self:
        return self

    def __deepcopy__(
        self, memo: typing.MutableMapping[int, typing.Any]
    ) -> typing_extensions.Self:
        memo[id(self)] = self
        return self


NOTHING = NothingType()
NothingType.__new__ = __new__
del __new__

_T = typing.TypeVar("_T")
NothingOr = typing.Union[_T, NothingType]
