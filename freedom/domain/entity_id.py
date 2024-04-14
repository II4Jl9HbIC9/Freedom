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
import typing
import uuid

from freedom.domain.valueobject import ValueObject


class EntityId(ValueObject, abc.ABC):
    __slots__: typing.Sequence[str] = ()

    def __init__(self, int: int) -> None:
        self._int = int

    @classmethod
    @abc.abstractmethod
    def next_id(cls, **kwargs: typing.Any) -> EntityId: ...

    @property
    def int(self) -> int:
        return self._int

    @property
    def str(self) -> str:
        return str(self.int)


class EntityIdUuid4(EntityId):
    @classmethod
    def next_id(cls, **kwargs: typing.Any) -> EntityIdUuid4:
        return cls(int=uuid.uuid4().int)


class EntityIdSequential(EntityId):
    @classmethod
    def next_id(cls, **kwargs: typing.Any) -> EntityIdSequential:
        next_id = kwargs.pop("next_id")
        if isinstance(next_id, int):
            return cls(int=next_id)
        return cls(int=int(next_id))
