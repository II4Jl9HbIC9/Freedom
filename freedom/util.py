from __future__ import annotations

import abc
import asyncio
import inspect
import sys
import typing

from freedom import sentinel

FROZEN_STR: typing.Final[str] = "__frozen__"
UNFREEZE_ATTRS_STR: typing.Final[str] = "__unfreeze_attrs__"

_T = typing.TypeVar("_T")


def __frozen_setattr__(
    self: typing.Any,
    key: typing.Any,
    value: typing.Any,
) -> None:
    if (
        self.__frozen__
        and sys._getframe().f_back.f_code.co_name not in self.__unfreeze_attrs__
    ):
        raise ImmutableObjectError("Object is immutable.")

    if hasattr(self, "__dict__"):
        self.__dict__[key] = value
        return

    object.__setattr__(self, key, value)


def __frozen_delattr__(self: typing.Any, item: typing.Any) -> None:
    if (
        self.__frozen__
        and sys._getframe().f_back.f_code.co_name not in self.__unfreeze_attrs__
    ):
        raise ImmutableObjectError("Object is immutable.")

    object.__delattr__(self, item)


async def empty_coro(*_: typing.Any, **__: typing.Any) -> typing.Any:
    pass


def get_loop() -> asyncio.AbstractEventLoop:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.get_event_loop_policy().get_event_loop()

    return loop


def as_completed_future(
    result: typing.Optional[_T] = None,
) -> asyncio.Future[typing.Optional[_T]]:
    future = get_loop().create_future()
    future.set_result(result)
    return future


def get_type_hints(
    obj: typing.Any,
    *,
    subclass_of: typing.Optional[typing.Tuple[typing.Type[typing.Any], ...]] = None,
) -> typing.Dict[str, typing.Type[typing.Any]]:
    hints = {
        k: (
            v.annotation
            if v.annotation is not inspect.Parameter.empty
            else sentinel.NOTHING
        )
        for k, v in inspect.Signature.from_callable(obj).parameters.items()
    }
    hints.update(typing.get_type_hints(obj))

    if subclass_of is not None:
        hints = {
            k: v
            for k, v in hints.items()
            if inspect.isclass(v) and issubclass(v, subclass_of)
        }

    return hints


def unpack_unions(
    hints: typing.Dict[str, typing.Type[typing.Any]],
) -> typing.Dict[str, typing.Type[typing.Any]]:
    unions = {}

    def _unpack_item(
        key: str,
        union_value: typing.Any,
        mapping: typing.Dict[str, typing.List[typing.Type[typing.Any]]],
    ) -> None:
        if key not in mapping:
            mapping[key] = []

        args = typing.get_args(union_value)
        for arg in args:
            if typing.get_origin(arg) is typing.Union:
                _unpack_item(key, arg, mapping)

            mapping[key].append(arg)

    for k, v in hints.items():
        if typing.get_origin(v) is typing.Union:
            _unpack_item(k, v, unions)

    hints.update(unions)
    return hints


def get_base_args(
    obj: typing.Any,
    base_type: typing.Type[typing.Any],
) -> typing.Tuple[typing.Type[typing.Any], ...]:
    bases = typing.cast(
        typing.Union[typing.Tuple[typing.Type[typing.Any], ...], None],
        getattr(obj, "__orig_bases__", None),
    )
    if bases is None:
        raise AttributeError(f"Cant find orig bases in obj {obj!r}")

    for base in bases:
        if (orig := typing.get_origin(base)) is None:
            # get_base_arg can handle only parametrized generics
            continue

        if orig is base_type:
            args = getattr(base, "__args__", ())
            return args

    raise ValueError(f"Cant find base that matches {base_type!r}")


class ImmutableObjectError(Exception):
    pass


class ImmutableMeta(abc.ABCMeta):
    def __new__(
        mcs: typing.Type[ImmutableMeta],
        name: str,
        bases: typing.Tuple[typing.Type[typing.Any], ...],
        attrs: typing.Dict[str, typing.Any],
    ) -> typing.Any:
        frozen = attrs.pop(FROZEN_STR, True)
        unfreeze = attrs.pop(UNFREEZE_ATTRS_STR, ())
        unfreeze += ("__frozen_setattr__", "__frozen_delattr__", "__init__")

        #
        attrs[UNFREEZE_ATTRS_STR] = unfreeze
        attrs[FROZEN_STR] = frozen

        attrs["__setattr__"] = attrs["__setitem__"] = __frozen_setattr__
        attrs["__delattr__"] = attrs["__delitem__"] = __frozen_delattr__
        return super().__new__(mcs, name, bases, attrs)
