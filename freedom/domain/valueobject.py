from __future__ import annotations

import typing

from freedom import util


class ValueObject(metaclass=util.ImmutableMeta):
    @classmethod
    def unfreeze(cls) -> None:
        setattr(cls, util.FROZEN_STR, False)

    @classmethod
    def freeze(cls) -> None:
        setattr(cls, util.FROZEN_STR, True)

    @classmethod
    def is_frozen(cls) -> bool:
        is_frozen = typing.cast(bool, getattr(cls, util.FROZEN_STR, False))
        return is_frozen
