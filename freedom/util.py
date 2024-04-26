# -*- coding: utf-8 -*-
# Copyright (c) 2024 II4Jl9HbIC9
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
from __future__ import annotations

import abc
import sys
import typing

FROZEN_STR: typing.Final[str] = "__frozen__"
UNFREEZE_ATTRS_STR: typing.Final[str] = "__unfreeze_attrs__"


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
