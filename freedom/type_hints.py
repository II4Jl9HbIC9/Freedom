from __future__ import annotations

__all__: typing.Sequence[str] = (
    "SysExcInfo",
    "OptionalSysExcInfo",
)

import types
import typing

import typing_extensions as typingext

SysExcInfo: typingext.TypeAlias = typing.Tuple[
    typing.Type[BaseException], BaseException, types.TracebackType
]
OptionalSysExcInfo: typingext.TypeAlias = typing.Union[
    SysExcInfo, typing.Tuple[None, None, None]
]
