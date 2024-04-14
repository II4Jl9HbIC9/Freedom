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

from freedom.domain.valueobject import ValueObject


class BusinessRule(ValueObject, abc.ABC):
    @abc.abstractmethod
    def is_broken(self) -> bool: ...

    @abc.abstractmethod
    def render_broken_rule(self) -> str: ...


class BusinessRuleValidationMixin:
    __slots__: typing.Sequence[str] = ()

    def check_rules(self, *rules: BusinessRule) -> None:
        violated_rules = []
        for rule in rules:
            if rule.is_broken():
                violated_rules.append(rule)

        if violated_rules:
            raise BusinessRuleValidationError(*violated_rules)


class BusinessRuleValidationError(Exception):
    __slots__: typing.Sequence[str] = ("_rules",)

    def __init__(self, *rules: BusinessRule) -> None:
        self._rules = rules
        super().__init__(self._render_broken_rules())

    def _render_broken_rules(self) -> str:
        broken_rules = ",".join(type(rule).__name__ for rule in self._rules)
        return f"Rules {broken_rules!r} are broken."
