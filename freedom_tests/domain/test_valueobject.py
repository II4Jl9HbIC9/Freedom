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

import pytest_bdd as ts  # technical specifications
from hamcrest import assert_that
from hamcrest import calling
from hamcrest import raises
from hamcrest import not_

from freedom import util
from freedom.domain import valueobject


class ImmutableValueObject(valueobject.ValueObject):
    # By default value objects are immutable
    pass


class PredefinedMutableValueObject(valueobject.ValueObject):
    __unfreeze_attrs__ = ("defrosted_method",)

    def __init__(self) -> None:
        self.awesome_attribute = ":)"

    def frozen_method(self) -> None:
        self.awesome_attribute = ":("

    def defrosted_method(self) -> None:
        self.awesome_attribute = ">:D"


class MutableValueObject(valueobject.ValueObject):
    __frozen__ = False


class DynamicallyMutableValueObject(valueobject.ValueObject):
    pass


@ts.scenario("valueobject.feature", "Immutable value object")
def test_immutable_value_object() -> None:
    pass


@ts.given(
    "an immutable value object",
    target_fixture="immutable_value_object",
)
def _() -> ImmutableValueObject:
    value_object = ImmutableValueObject()
    return value_object


@ts.when("we try to change its state")
@ts.then("an exception is raised notifying us that the object is immutable")
def _(immutable_value_object: ImmutableValueObject) -> None:
    def modify_state() -> None:
        immutable_value_object.awesome_attribute = "^_^"

    assert_that(
        calling(modify_state),
        raises(util.ImmutableObjectError)
    )


@ts.scenario(
    "valueobject.feature",
    "Predefined methods for modifying state of value object",
)
def test_predefined_mutable_value_object() -> None:
    pass


@ts.given(
    "an immutable value object with predefined methods for modifying its state",
    target_fixture="predefined_value_object",
)
def _() -> PredefinedMutableValueObject:
    value_object = PredefinedMutableValueObject()
    return value_object


@ts.when("we change its state in a method that does not have access to modify the state")
@ts.then("an exception is raised informing us that the object is immutable")
def _(predefined_value_object: PredefinedMutableValueObject) -> None:
    def modify_state() -> None:
        predefined_value_object.frozen_method()

    assert_that(
        calling(modify_state),
        raises(util.ImmutableObjectError),
    )


@ts.when("we change its state in a method that has access to modify the state")
@ts.then("no errors are raised")
def _(predefined_value_object: PredefinedMutableValueObject) -> None:
    def modify_state() -> None:
        predefined_value_object.defrosted_method()

    assert_that(
        calling(modify_state),
        not_(
            raises(util.ImmutableObjectError)
        )
    )


@ts.scenario("valueobject.feature", "Mutable value object")
def test_mutable_value_object() -> None:
    pass


@ts.given(
    "a value object that is defined as mutable",
    target_fixture="mutable_value_object",
)
def _() -> MutableValueObject:
    value_object = MutableValueObject()
    return value_object


@ts.when("we change its state")
@ts.then("no exceptions are raised")
def _(mutable_value_object: MutableValueObject) -> None:
    def modify_state() -> None:
        mutable_value_object.new_awesome_attribute = "0_0"

    assert_that(
        calling(modify_state),
        not_(
            raises(util.ImmutableObjectError)
        ),
    )


@ts.scenario("valueobject.feature", "Dynamically mutable value object")
def test_dynamically_mutable_value_object() -> None:
    pass


@ts.given(
    "an immutable value object by default",
    target_fixture="dynamically_mutable_value_object",
)
def _() -> DynamicallyMutableValueObject:
    value_object = DynamicallyMutableValueObject()
    return value_object


@ts.when("we unfreeze the immutable value object")
@ts.then("no errors are raised when changing the state")
@ts.when("we freeze the mutable value object")
@ts.when("we change the state of this value object")
@ts.then("an error is raised informing us that the value object is immutable")
def _(dynamically_mutable_value_object: DynamicallyMutableValueObject) -> None:
    def modify_state() -> None:
        dynamically_mutable_value_object.new_awesome_attribute = "=_="

    dynamically_mutable_value_object.unfreeze()

    assert_that(
        calling(modify_state),
        not_(
            raises(util.ImmutableObjectError)
        ),
    )

    dynamically_mutable_value_object.freeze()

    assert_that(
        calling(modify_state),
        raises(util.ImmutableObjectError),
    )
