"""Test usage of injectables via decorators instead of imperative.

More cumbersome (due to scanner) to copy around so placed into a
single test.
"""
from dataclasses import dataclass
from typing import cast

import pytest

from hopscotch import Registry, Registration
from hopscotch import injectable
from hopscotch.fixtures import dataklasses
from hopscotch.fixtures.dataklasses import Customer
from hopscotch.fixtures.dataklasses import FrenchCustomer
from hopscotch.fixtures.dataklasses import Greeter
from hopscotch.fixtures.dataklasses import GreeterCustomer
from hopscotch.fixtures.dataklasses import GreeterFrenchCustomer


class View:
    """A marker for an example View custom injectable."""

    title: str


# noinspection PyPep8Naming
class view(injectable):  # noqa: N801
    """Custom decorator for custom injectable."""

    kind = View


class Config:
    """A marker for an example singleton custom injectable."""

    title: str


# noinspection PyPep8Naming
class config(injectable):  # noqa: N801
    """Custom decorator for custom singleton injectable."""

    kind = Config
    is_singleton = True


@view()
@dataclass
class MyView(View):
    """An example view."""

    title: str = "My View"


@config()
@dataclass
class MyConfig(View):
    """An example configuration."""

    title: str = "My Config"


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


def test_custom_decorator() -> None:
    """Test the custom view decorator."""
    registry = Registry()
    registry.scan()
    result = cast(MyView, registry.get(View))
    assert "My View" == result.title


def test_custom_singleton_decorator() -> None:
    """Test the custom singleton decorator."""
    registry = Registry()
    registry.scan()
    config_singletons = registry.registrations[Config]["singletons"]
    items = cast(list, list(config_singletons.values())[0])
    first: Registration = items[0]
    impl = cast(MyConfig, first.implementation)
    assert "My Config" == impl.title
    result = cast(MyConfig, registry.get(Config))
    assert "My Config" == result.title
