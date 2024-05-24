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
