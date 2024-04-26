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

Feature: ValueObject
  """
  Value objects are a fundamental concept in Domain-Driven Design (DDD). They are used to
  represent descriptive aspects of the domain and do not have an independent identity.
  Value objects are created in the program to represent those elements of the project for
  which it is sufficient to know what they represent, but not who they ARE.

  when modeling a domain concept as a VALUE OBJECT, the first thing to do is to make sure
  that you are using a UBIQUITOUS LANGUAGE. When deciding whether a concept is a VALUE,
  you should consider whether it has most of the following characteristics:

  1. It measures, evaluates, or describes a domain object.
     A true VALUE OBJECT in the model is not a domain object. In fact, it is a concept
     that measures, quantifies, or otherwise describes a domain object.
  2. It models something conceptually whole, combining related attributes into a single
     unit.
     The attributes that form a VALUE OBJECT together must be a single conceptual whole
     (WHOLE VALUE). A VALUE OBJECT can have one, several, or many individual attributes,
     each of which is related to the others. Each attribute makes an important
     contribution to the whole that these attributes describe together.

     Taken individually, each of the attributes does not provide a consistent description.
     Only all the attributes taken together form a complete measure or description. This
     is what distinguishes them from a simple grouping of attributes within an object.

     If the whole does not adequately describe the entity in the model, then the grouping
     itself means little [Ward Cunningham].
  3. It provides its associated objects with a SIDE EFFECT-FREE FUNCTION. A method inside
     an object can be designed as a SIDE EFFECT-FREE FUNCTION. A function is an operation
     on an object that produces a result but does not modify its state. If a particular
     operation does not modify the object, it is called a side effect-free operation.

     All methods of an immutable VALUE OBJECT must be SIDE EFFECT-FREE FUNCTIONS, because
     they must not violate the immutability property. The absence of side effects and
     immutability are closely related.

     However, it is worth considering them as separate characteristics to emphasize the
     enormous benefit of using VALUE OBJECTS. Otherwise, VALUES may turn out to be simple
     attribute containers, losing much of the advantage of this pattern.
  4. It can be completely replaced when the way it is measured or described is changed.
  5. It can be compared to other objects using a VALUE equality relationship.
  6. It can be considered immutable.

  Note
  ----
  Special cases: when to allow mutability?

  The immutability of objects greatly simplifies the software implementation, guaranteeing
  the safety of sharing and passing references. It also follows the idea of objects as
  values. If the value of some attribute changes, then instead of modifying the existing
  VALUE OBJECT, a new one is simply used. But there are cases where, for performance
  reasons, it is better to allow changes to VALUE OBJECTS.

  The following factors usually speak in favor of this:
    • frequent changes in the object's value (i.e., the VALUE OBJECT itself);
    • the cost of creating and destroying an object;
    • the danger of replacement (instead of modification) when grouping objects, as was
      shown in the previous example;
    • insignificant or no sharing at all in order to improve object grouping or for other
      technical reasons.

  It is worth repeating that if the implementation of a VALUE OBJECT is assumed to be
  mutable, such an object should not be shared with another object. But regardless of
  whether they will be shared or not, do not change VALUE OBJECTS whenever possible.

  Info
  ----
  Are all VALUE OBJECTS?

  One might suspect that everything around is VALUE OBJECTS. This is still better than
  thinking that everything around is ENTITIES. Some caution should be exercised in
  situations where there are indeed simple attributes that do not require special
  handling.

  Perhaps these are Boolean types or numeric values that are truly self-sufficient, do not
  require additional functional support, and are not associated with any other attributes
  of the same ENTITY. Such simple attributes represent a MEANINGFUL WHOLE.

  However, you can "mistakenly" wrap a single attribute into a VALUE type without special
  functionality, and this is better than never using VALUES. When you realize that you
  have made a mistake, you can always do a little refactoring.
  """

  Scenario: Immutable value object
    Given an immutable value object
    When we try to change its state
    Then an exception is raised notifying us that the object is immutable

  Scenario: Predefined methods for modifying state of value object
    Given an immutable value object with predefined methods for modifying its state
    When we change its state in a method that does not have access to modify the state
    Then an exception is raised informing us that the object is immutable
    When we change its state in a method that has access to modify the state
    Then no errors are raised

  Scenario: Mutable value object
    Given a value object that is defined as mutable
    When we change its state
    Then no exceptions are raised

  Scenario: Dynamically mutable value object
    """
    This approach can be quite dangerous and unpredictable, as objects can be thawed and
    frozen in any state, whether it is a class or its instance, and also in any part of
    the code.

    However, the changes will be applied to the class itself, which can affect all
    existing DIRECT instances of the mutable class.

    Since the application architecture is mainly designed in advance, the fact that a
    particular value object is mutable is better to indicate EXPLICITLY in advance
    (by overriding the corresponding class attributes when writing it).
    """
    Given an immutable value object by default
    When we unfreeze the immutable value object
    Then no errors are raised when changing the state
    When we freeze the mutable value object
    And we change the state of this value object
    Then an error is raised informing us that the value object is immutable
