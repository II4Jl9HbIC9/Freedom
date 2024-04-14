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

__all__: typing.Sequence[str] = ("subclass_of",)

import typing

from hamcrest.core import base_matcher

if typing.TYPE_CHECKING:
    from hamcrest.core import description as description_


class IsSubclassOf(base_matcher.BaseMatcher):
    def __init__(
        self,
        cls_or_tuple: typing.Union[typing.Type[typing.Any], tuple[typing.Type[typing.Any], ...]], /
    ) -> None:
        self._cls_or_tuple = cls_or_tuple
        self.failed: typing.Optional[str] = None

    def _matches(self, cls: typing.Type[typing.Any]) -> bool:
        result = issubclass(cls, self._cls_or_tuple)
        if not result:
            self.failed = cls

        return result

    def describe_to(self, description: description_.Description) -> None:
        (
            description.append_text("failing on ")
            .append_text(f"<{self.failed}> attribute")
        )


def subclass_of(
    cls_or_tuple: typing.Union[typing.Type[typing.Any], tuple[typing.Type[typing.Any], ...]], /
) -> IsSubclassOf:
    return IsSubclassOf(cls_or_tuple)
