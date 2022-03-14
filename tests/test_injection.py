"""Test the injection process.

The ``inject_callable`` callable is used in both the registry and
components. Thus it needs to support use both with and without a
registry.
"""
from dataclasses import dataclass

import pytest
from hopscotch import Registry
from hopscotch.fixtures import functions
from hopscotch.fixtures import named_tuples
from hopscotch.fixtures.dataklasses import AnotherGreeting
from hopscotch.fixtures.dataklasses import Customer
from hopscotch.fixtures.dataklasses import Greeter
from hopscotch.fixtures.dataklasses import GreeterCustomer
from hopscotch.fixtures.dataklasses import GreeterKind
from hopscotch.fixtures.dataklasses import GreeterRegistry
from hopscotch.fixtures.dataklasses import Greeting
from hopscotch.fixtures.dataklasses import GreetingFactory
from hopscotch.fixtures.dataklasses import GreetingFieldDefault
from hopscotch.fixtures.dataklasses import GreetingFieldDefaultFactory
from hopscotch.fixtures.dataklasses import GreetingNoDefault
from hopscotch.registry import inject_callable
from hopscotch.registry import Registration


def test_field_default() -> None:
    """The target is a field with a default."""
    registration = Registration(Greeting)
    result: Greeting = inject_callable(registration)
    assert result.salutation == "Hello"


def test_field_default_argument() -> None:
    """The target is a field using a default argument."""
    registration = Registration(GreetingFieldDefault)
    result: Greeting = inject_callable(registration)
    assert result.salutation == "Default Argument"


def test_field_default_factory() -> None:
    """The target is a field using a default factory."""
    registration = Registration(GreetingFieldDefaultFactory)
    result: Greeting = inject_callable(registration)
    assert result.salutation == []


def test_dependency_class() -> None:
    """The target has a field dependency to fetch from registry."""
    registry = Registry()
    registry.register(Greeting)

    registration = Registration(GreeterKind)
    result: GreeterKind = registry.inject(registration)
    assert "Hello" == result.greeting.salutation


def test_dependency_default_class() -> None:
    """The target has a field dependency NOT in registry."""

    @dataclass
    class SomeSalutation:
        title: str = "Some Salutation"

    @dataclass
    class SomeGreeting:
        some_salutation: SomeSalutation = SomeSalutation()

    registry = Registry()

    registry.register(SomeGreeting)
    registry.register(SomeGreeting)
    registration = Registration(SomeGreeting)
    result: SomeGreeting = registry.inject(registration)
    assert "Some Salutation" == result.some_salutation.title


def test_dependency_namedtuple() -> None:
    """Inject a non-type that isn't registered.

    We use ``registry.get`` to get an implementation that is a type of
    the thing we are looking up. Things like ``NamedTuple`` and
    functions can't be subclasses.

    They can still be used by the injector, just by grabbing the symbol
    directly rather than going to find it.
    """
    registration = Registration(named_tuples.Greeter)
    result: Greeter = inject_callable(registration)
    assert "Hello" == result.greeting.salutation


def test_inject_function_no_type_hint() -> None:
    """A function parameter with no type hint can use default value."""
    registration = Registration(functions.GreetingDefaultNoHint)
    result: str = inject_callable(registration)
    assert "Hello" == result


def test_inject_function_injectable() -> None:
    """A function parameter with type hint in registry."""
    customer = Customer(first_name="Marie")
    registry = Registry()
    registry.register(customer)
    registration = Registration(functions.GreeterRegisteredType)
    result: Customer = inject_callable(registration, registry=registry)
    assert "Marie" == result.first_name


def test_injection_no_registry() -> None:
    """Simulate usage of injection rules without needing a registry."""
    props = dict(salutation="No registry")
    registration = Registration(Greeting)
    result: Greeting = inject_callable(registration, props=props)
    assert "No registry" == result.salutation


def test_dependency_no_default() -> None:
    """The target has str field with no default, fail with custom exception."""
    registration = Registration(GreetingNoDefault)
    with pytest.raises(ValueError) as exc:
        inject_callable(registration)

    expected = "Cannot inject 'str' on 'GreetingNoDefault.salutation'"
    assert exc.value.args[0] == expected


def test_dependency_default() -> None:
    """The target has an str field with a default."""
    registration = Registration(AnotherGreeting)
    result: AnotherGreeting = inject_callable(registration)
    assert "Another Hello" == result.salutation


def test_non_dependency() -> None:
    """The target has a dependent field to fetch from registry."""
    gs = Greeting(salutation="use singleton")
    registry = Registry()
    registry.register(gs)
    registration = Registration(Greeter)
    result: Greeter = inject_callable(registration, registry=registry)
    assert "use singleton" == result.greeting.salutation


def test_dependency_nested_registry() -> None:
    """Nested registry, can injector get singleton from right level?"""
    gs_child = Greeting(salutation="use child")
    gs_parent = Greeting(salutation="use parent")

    # Site registry
    parent_registry = Registry()
    parent_registry.register(gs_parent)

    # Per-request registry with a specific singleton
    child_registry = Registry(parent=parent_registry)
    child_registry.register(gs_child)

    # Get something registered with parent, dependency local
    registration = Registration(GreeterKind)
    result: GreeterKind = child_registry.inject(registration)
    assert "use child" == result.greeting.salutation


def test_pass_in_props_create_dependency() -> None:
    """Instead of injecting a field, get it from passed-in 'props'."""
    props = dict(salutation="use prop")
    registration = Registration(Greeting)
    result: Greeting = inject_callable(registration, props=props)
    assert result.salutation == "use prop"


def test_inject_registry() -> None:
    """Target wants the registry and will later get what it needs."""
    registry = Registry()
    registration = Registration(GreeterRegistry)
    result: GreeterRegistry = inject_callable(registration, registry=registry)
    assert registry == result.registry


def test_inject_context() -> None:
    """Target wants the registry context."""
    customer = Customer(first_name="Mary")
    registry = Registry(context=customer)
    registration = Registration(GreeterCustomer)
    registry.register(GreeterCustomer)
    result: GreeterCustomer = inject_callable(registration, registry=registry)
    assert customer == result.customer


def test_hopscotch_factory() -> None:
    """The dependency has its own factory as a class attribute."""
    r = Registration(GreetingFactory)
    registry = Registry()
    registry.register(GreetingFactory)
    result: GreetingFactory = inject_callable(r, registry=registry)
    assert result.salutation == "Hi From Factory"
