"""

Test usage of wired and components via decorators instead of
imperative.

More cumbersome (due to scanner) to copy around so placed into a
single test.

"""
import pytest

from hopscotch.fixtures import dataklasses
from hopscotch.fixtures.dataklasses import Greeter, Customer, GreeterCustomer, FrenchCustomer, GreeterFrenchCustomer
from hopscotch.registry import Registry


def test_injectable_no_context() -> None:
    """The decorator and its registration do not care about context."""
    registry = Registry()
    registry.scan(dataklasses)
    greeter = registry.get(Greeter)
    assert greeter.greeting.salutation == "Hello"


def test_injectable_context() -> None:
    """The decorator has no context but the registration wants it."""
    customer = Customer(first_name="Fred")
    registry = Registry(context=customer)
    registry.scan(dataklasses)
    greeter = registry.get(GreeterCustomer)
    assert greeter.customer.first_name == "Fred"


def test_injectable_explicit_context() -> None:
    """A registration for a specific context."""
    french_customer = FrenchCustomer(first_name="Marie")

    # First, a registry that has a FrenchCustomer context.
    registry = Registry(context=french_customer)
    registry.scan(dataklasses)
    greeter = registry.get(GreeterFrenchCustomer)
    assert greeter.customer.first_name == "Marie"

    # This registry that has no FrenchCustomer context.
    registry2 = Registry()
    registry2.scan(dataklasses)
    with pytest.raises(LookupError):
        registry2.get(GreeterFrenchCustomer)
