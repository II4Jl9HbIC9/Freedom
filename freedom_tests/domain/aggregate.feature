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

Feature: AggregateRoot
  In Domain-Driven Design (DDD), an Aggregate Root is the primary access point to
  the domain model. It represents a cluster of related domain objects, treated as
  a single unit to enforce business rules and maintain consistency.

  Aggregates encapsulate internal state and behavior, managing the lifecycle of
  domain objects. They ensure that objects outside the aggregate cannot directly
  access or modify its internal state.

  Changes to objects within an aggregate are transactional, ensuring either all
  changes are applied or none are, maintaining aggregate consistency in case of failure.

  Note
  ----
  Aggregates should reference other aggregates (Entities) but not contain them.
  Aggregates are designed based on the problem space, not technical considerations.

  Scenario: Ensuring Consistency and Integrity
    Aggregates ensure that their internal objects are always in a consistent state.
    By encapsulating internal state and behavior, aggregates provide a clear boundary
    for managing business rules.

    Given a Task aggregate
      """
      Task represents a task in a TODO application. Aggregate encapsulates
      access to attributes like title, a collection of Tag aggregate IDs, and a collection
      of comments. Also Task follows the TaskTitleLengthRule business rule
      """

    And a Tag aggregate
      """
      Tag is a separate aggregate with its own lifecycle, independent
      of a aggregate Task
      """

    And a Comment entity, meaningful only within a task
    # note: Comments can also be implemented as ValueObjects if they are immutable

    And a TaskTitleLengthRule defining valid title lengths for a Task

    When setting a task title that satisfies TaskTitleLengthRule
    Then no exception is thrown

    When setting a Task title that violates TaskTitleLengthRule
    Then an exception is thrown, indicating a violation of the TaskTitleLengthRule

  Scenario: Initiating Domain Events
    - When an aggregate records a fact that has occurred, it is said to initiate an event.
    Instead of directly calling code (e.g., sending notifications), we record these events
    where they occur, using only the domain language.

    This approach also helps to eliminate exceptions in the domain. Events perform their work
    instead. "Exceptions as control flow" is a known anti-pattern.

    The idea of exceptions is that:
      1. We raise an error if we don't know how to handle it properly, because we don't
         have enough context to process it.
      2. We have just encountered a serious unexpected error, and exiting this control
         flow right now is more important than trying to continue, to prevent data corruption
         or other damage.

      These statements contradict the concept of the domain, so we should not complicate the
      business layer with this approach.

      # TODO: Should we implement versioning in the domain or is this a task for other
      #       services or infrastructure solutions?

    Given a User aggregate exists

    When the user's nickname is changed

    Then a UserNicknameChanged event is registered with the User aggregate
    And all unprocessed events for the User aggregate can be retrieved
