"""Test the injection process.

The ``inject_callable`` callable is used in both the registry and
components. Thus it needs to support use both with and without a
registry.
"""
import pytest

from hopscotch.field_infos import get_field_infos
from hopscotch.fixtures.dataklasses import (
    GreetingService,
    GreeterService,
    Greeter,
    GreetingNoDefault,
    Greeting,
    GreetingImplementer,
    GreetingFactory,
    GreeterRegistry,
    GreeterCustomer,
    Customer,
)
from hopscotch.registry import Registry, inject_callable, Registration


def test_field_default() -> None:
    """The target a field with a default."""
    registration = Registration(GreetingService)
    result = inject_callable(registration)
    assert result.salutation == "Hello"


def test_service_dependency_class() -> None:
    """The target has a field dependency to fetch from registry."""
    registry = Registry()
    registry.register_service(GreetingService)

    registration = Registration(GreeterService)
    result = registry.inject(registration)
    assert "Hello" == result.greeting.salutation


def test_injection_no_registry() -> None:
    """Simulate usage of injection rules without needing a registry."""
    props = dict(salutation="No registry")
    registration = Registration(Greeting)
    result = inject_callable(registration, props=props)
    assert "No registry" == result.salutation


def test_service_dependency_no_default() -> None:
    """The target has str field with no default, fail with custom exception."""
    registration = Registration(GreetingNoDefault)
    with pytest.raises(ValueError) as exc:
        inject_callable(registration)

    expected = f"Cannot inject 'str' on 'GreetingNoDefault.salutation'"
    assert exc.value.args[0] == expected


def test_service_dependency_default() -> None:
    """The target has an str field with a default."""
    registration = Registration(GreetingImplementer)
    result = inject_callable(registration)
    assert "Hello" == result.salutation


def test_non_service_dependency() -> None:
    """The target has a non-service field to fetch from registry."""
    gs = Greeting(salutation="use singleton")
    registry = Registry()
    registry.register_singleton(gs)
    registration = Registration(Greeter)
    result = inject_callable(registration, registry=registry)
    assert "use singleton" == result.greeting.salutation


def test_service_dependency_nested_registry() -> None:
    """Nested registry, can service get singleton from right level?"""

    gs_child = GreetingService(salutation="use child")
    gs_parent = GreetingService(salutation="use parent")

    # Site registry
    parent_registry = Registry()
    parent_registry.register_singleton(gs_parent)

    # Per-request registry with a specific singleton
    child_registry = Registry(parent=parent_registry)
    child_registry.register_singleton(gs_child)

    # Get something registered with parent, dependency local
    registration = Registration(GreeterService)
    result = child_registry.inject(registration)
    assert "use child" == result.greeting.salutation


def test_pass_in_props_create_service() -> None:
    """Instead of injecting a field, get it from passed-in 'props'."""
    props = dict(salutation="use prop")
    registration = Registration(Greeting)
    result = inject_callable(registration, props=props)
    assert result.salutation == "use prop"


def test_inject_registry() -> None:
    """Target wants the registry and will later get what it needs."""
    registry = Registry()
    registration = Registration(GreeterRegistry)
    result = inject_callable(registration, registry=registry)
    assert registry == result.registry


def test_inject_context() -> None:
    """Target wants the registry context."""
    customer = Customer(first_name="Mary")
    registry = Registry(context=customer)
    registration = Registration(GreeterCustomer)
    registry.register_service(GreeterCustomer)
    result = inject_callable(registration, registry=registry)
    assert customer == result.customer


def test_hopscotch_factory() -> None:
    """The service has its own factory as a class attribute."""
    registraton = Registration(GreetingFactory)
    registry = Registry()
    registry.register_service(GreetingFactory)
    result = inject_callable(registraton, registry=registry)
    assert result.salutation == "Hi From Factory"
