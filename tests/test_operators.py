"""Test the bundled operators."""
from dataclasses import dataclass
from hopscotch import Registry
from hopscotch.fixtures.dataklasses import Greeting
from hopscotch.operators import Context
from hopscotch.operators import Get
from hopscotch.operators import make_field_operator
from typing import Annotated

import pytest


def test_get_setup() -> None:
    """Setup a ``Get`` operator."""
    get = Get(Greeting)
    assert Greeting == get.lookup_key
    assert None is get.attr


def test_get_setup_attr() -> None:
    """Setup a ``Get`` operator with an attr."""
    get = Get(Greeting, attr="salutation")
    assert Greeting == get.lookup_key
    assert "salutation" == get.attr


def test_operators_get_simple_type() -> None:
    """Use Annotated to lookup one type while stating another."""

    @dataclass()
    class DummyGreeter:
        dummy_greeting: Annotated[Greeting, Get(Greeting)]

    registry = Registry()
    greeting = Greeting()
    registry.register(greeting)
    registry.register(DummyGreeter)
    # Now ask the registry to construct this
    dummy_greeter = registry.get(DummyGreeter)
    assert isinstance(dummy_greeter.dummy_greeting, Greeting)


def test_operators_get_attr() -> None:
    """Use Get with attr to pluck an attribute off the injected target."""

    @dataclass()
    class DummyGreeter:
        dummy_salutation: Annotated[str, Get(Greeting, "salutation")]

    registry = Registry()
    greeting = Greeting()
    registry.register(greeting)
    registry.register(DummyGreeter)
    # Now ask the registry to construct this
    dummy_greeter = registry.get(DummyGreeter)
    assert "Hello" == dummy_greeter.dummy_salutation


def test_operators_get_failed_string() -> None:
    """Operators can never look up a string in the registry."""
    registry = Registry()
    get = Get("Failure")
    expected = "Cannot use a string 'Failure' as container lookup value"
    with pytest.raises(ValueError) as exc:
        get(registry)
    assert exc.value.args[0] == expected


def test_operators_get_value_none() -> None:
    """Registry did not have the lookup key registered as a kind."""
    registry = Registry()
    get = Get(Greeting)
    with pytest.raises(LookupError) as exc:
        get(registry)
    expected = "No kind 'Greeting' in registry"
    assert exc.value.args[0] == expected


def test_operators_context_setup() -> None:
    """Ensure the context operator can be constructed."""
    context = Context(attr="title")
    assert context.attr == "title"


def test_operators_context() -> None:
    """Get the current registry context."""

    @dataclass
    class Context1:
        title: str = "Context 1"

    @dataclass
    class DummyHeading:
        context1: Annotated[Context1, Context()]

    context1 = Context1()
    registry = Registry(context=context1)
    registry.register(DummyHeading)
    result = registry.get(DummyHeading)
    assert result.context1 == context1


def test_operators_context_attr() -> None:
    """Pluck an attr off the registry context."""

    @dataclass
    class Context1:
        title: str = "Context 1"

    @dataclass
    class DummyHeading:
        context_title: Annotated[
            str,
            Context(attr="title"),  # noqa: F821
        ]

    context1 = Context1()
    registry = Registry(context=context1)
    registry.register(DummyHeading)
    result = registry.get(DummyHeading)
    assert result.context_title == context1.title


def test_operators_operators_value_none() -> None:
    """Registry did not have the lookup key."""
    context = Context()
    with pytest.raises(ValueError) as exc:
        context(Registry())
    expected = "No context on registry"
    assert exc.value.args[0] == expected


def test_make_field_operator() -> None:
    """Turn an operator into a dataclass field."""
    get = make_field_operator(Get)
    get_field = get(Greeting, attr="salutation", metadata=dict(flag=9))
    metadata = get_field.metadata
    assert metadata["flag"] == 9
    injected = metadata["injected"]
    operator: Get = injected["operator"]
    assert operator.lookup_key == Greeting
    assert operator.attr == "salutation"
