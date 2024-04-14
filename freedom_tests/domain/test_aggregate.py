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

import functools
import typing

import pytest_bdd as ts  # technical specifications
from hamcrest import assert_that
from hamcrest import calling
from hamcrest import equal_to
from hamcrest import has_length
from hamcrest import instance_of
from hamcrest import not_
from hamcrest import raises

from freedom_tests.hamcrest_ext import subclass_of

from freedom.domain import aggregate
from freedom.domain import business_rule
from freedom.domain import entity
from freedom.domain import entity_id
from freedom.domain import event


class TaskTitleLengthRule(business_rule.BusinessRule):
    __slots__: typing.Sequence[str] = ("min_length", "max_length", "title",)

    def __init__(self, title: str, min_length: int, max_length: int) -> None:
        self.min_length = min_length
        self.max_length = max_length
        self.title = title

    def is_broken(self) -> bool:
        is_satisfied = (self.min_length <= len(self.title) <= self.max_length)
        return not is_satisfied

    def render_broken_rule(self) -> str:
        message = (
            "The title length exceeds the established limit of {self.max_length} characters"
            " "
            "or the title length is less than one character"
        )
        return message


bounded_title_length_rule = functools.partial(
    TaskTitleLengthRule,
    min_length=1,
    max_length=15,
)


class TaskId(entity_id.EntityIdSequential):
    pass


class Task(aggregate.AggregateRoot[TaskId]):
    def __init__(self, id: TaskId, title: str = "Unknown") -> None:
        super().__init__(id=id)
        self._title = title

    def set_title(self, title: str) -> None:
        self.check_rules(bounded_title_length_rule(title))
        self._title = title


class TagId(entity_id.EntityIdUuid4):
    pass


class Tag(aggregate.AggregateRoot[TagId]):
    pass


class Comment(entity.Entity):
    pass


class CommentId(entity_id.EntityIdSequential):
    @classmethod
    def next_id(cls, **kwargs: typing.Any) -> CommentId:
        return cls(int=kwargs.pop("comment_number"))


@ts.scenario("aggregate.feature", "Ensuring Consistency and Integrity")
def test_consistency_and_integrity() -> None:
    pass


@ts.given(
"""a Task aggregate
Task represents a task in a TODO application. Aggregate encapsulates
access to attributes like title, a collection of Tag aggregate IDs, and a collection
of comments. Also Task follows the TaskTitleLengthRule business rule""",
    target_fixture="task",
)
def _() -> Task:
    task_id = TaskId(int=1)
    task = Task(id=task_id)
    return task


@ts.given(
"""a Tag aggregate
Tag is a separate aggregate with its own lifecycle, independent
of a aggregate Task""",
    target_fixture="tag",
)
def _() -> Tag:
    tag = Tag(id=TagId.next_id())
    return tag


@ts.given(
    "a Comment entity, meaningful only within a task",
    target_fixture="comment",
)
def _() -> Comment:
    comment = Comment(id=CommentId(int=1))
    return comment


@ts.given("a TaskTitleLengthRule defining valid title lengths for a Task")
def _() -> None:
    assert_that(
        TaskTitleLengthRule,
        subclass_of(business_rule.BusinessRule)
    )


@ts.when("setting a task title that satisfies TaskTitleLengthRule")
@ts.then("no exception is thrown")
def _(task: Task) -> None:
    assert_that(
        (
            calling(task.set_title)
            .with_args("Awesome title")
        ),
        not_(
            raises(business_rule.BusinessRuleValidationError)
        )
    )


@ts.when("setting a Task title that violates TaskTitleLengthRule")
@ts.then("an exception is thrown, indicating a violation of the TaskTitleLengthRule")
def _(task: Task) -> None:
    assert_that(
        (
            calling(task.set_title)
            .with_args("Some Very Long title...")
        ),
        raises(business_rule.BusinessRuleValidationError)
    )


class UserNicknameChanged(event.Event):
    def __init__(self, before: str, after: str) -> None:
        self.before = before
        self.after = after


class UserId(entity_id.EntityIdUuid4):
    pass


class User(aggregate.AggregateRoot[UserId]):
    def __init__(self, id: UserId, nickname: str) -> None:
        super().__init__(id=id)
        self._nickname = nickname

    def change_nickname(self, name: str) -> None:
        nickname_changed = UserNicknameChanged(
            before=self._nickname, after=name,
        )
        self.record_that(nickname_changed)


@ts.scenario("aggregate.feature", "Initiating Domain Events")
def test_initiating_domain_events() -> None:
    pass


@ts.given("a User aggregate exists", target_fixture="user")
def _() -> User:
    user = User(
        id=UserId.next_id(),
        nickname="Boba",
    )
    return user


@ts.when("the user's nickname is changed", target_fixture="modified_user")
def _(user: User) -> User:
    assert_that(user.uncommitted_events, has_length(0))
    user.change_nickname("Biba")
    assert_that(user.uncommitted_events, has_length(1))
    return user


@ts.then("a UserNicknameChanged event is registered with the User aggregate")
@ts.then("all unprocessed events for the User aggregate can be retrieved")
def _(modified_user: User) -> None:
    expected_event = UserNicknameChanged(before="Boba", after="Biba")
    expected_event_type = UserNicknameChanged
    assert_that(
        modified_user.uncommitted_events[0],
        instance_of(expected_event_type),
    )
    assert_that(
        modified_user.uncommitted_events[0].before,
        equal_to(expected_event.before),
    )
    assert_that(
        modified_user.uncommitted_events[0].after,
        equal_to(expected_event.after),
    )
