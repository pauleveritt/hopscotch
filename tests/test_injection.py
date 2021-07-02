"""Test the injection process.

The ``inject_callable`` callable is used in both the registry and
components. Thus it needs to support use both with and without a
registry.
"""
import pytest

from hopscotch.fixtures.dataklasses import GreetingService, GreeterService, Greeter, GreetingNoDefault, Greeting, \
    GreetingImplementer, GreetingFactory
from hopscotch.registry import Registry, inject_callable


def test_field_default() -> None:
    """The target a field with a default."""
    registry = Registry()
    result = registry.inject(GreetingService)
    assert result.salutation == "Hello"


def test_service_dependency_class() -> None:
    """The target has a field to fetch from registry."""
    registry = Registry()
    registry.register_service(GreetingService)
    result = registry.inject(GreeterService)
    assert "Hello" == result.greeting.salutation


def test_service_dependency_singleton() -> None:
    """Injection should find a singleton if it is registered."""
    registry = Registry()
    gs = GreetingService(salutation="use singleton")
    registry.register_singleton(gs)
    result = registry.inject(GreeterService)
    assert "use singleton" == result.greeting.salutation


def test_injection_no_registry() -> None:
    """Simulate usage of injection rules without needing a registry."""
    props = dict(salutation="No registry")
    result = inject_callable(Greeting, props=props, registry=None)
    assert "No registry" == result.salutation


def test_service_dependency_no_default() -> None:
    """The target has str field with no default, fail with custom exception."""
    registry = Registry()
    registry.register_service(GreetingNoDefault, servicetype=Greeting)
    with pytest.raises(ValueError) as exc:
        registry.inject(Greeter)

    target = "hopscotch.fixtures.dataklasses.Greeting"
    expected = f"Cannot inject <class '{target}'> on "'Greeter.greeting'
    assert exc.value.args[0] == expected


def test_service_dependency_default() -> None:
    """The target has an str field with a default."""
    registry = Registry()
    registry.register_service(GreetingImplementer, servicetype=GreetingService)
    result = registry.inject(GreeterService)
    assert "Hello" == result.greeting.salutation


def test_non_service_dependency() -> None:
    """The target has a non-service field to fetch from registry."""
    gs = Greeting(salutation="use singleton")
    registry = Registry()
    registry.register_singleton(gs)
    registry.register_service(Greeter)
    result = registry.get_service(Greeter)
    assert "use singleton" == result.greeting.salutation


def test_service_dependency_nested_registry() -> None:
    """ Nested registry, can service get singleton from right level? """

    gs_child = GreetingService(salutation="use child")
    gs_parent = GreetingService(salutation="use parent")

    # Site registry
    parent_registry = Registry()
    parent_registry.register_singleton(gs_parent)

    # Per-request registry with a specific singleton
    child_registry = Registry(parent=parent_registry)
    child_registry.register_singleton(gs_child)

    # Get something registered with parent, dependency local
    result = child_registry.inject(GreeterService)
    assert "use child" == result.greeting.salutation


def test_pass_in_props_create_service() -> None:
    """Instead of injecting a field, get it from passed-in 'props'."""
    registry = Registry()
    props = dict(salutation="use prop")
    result = registry.inject(Greeting, props=props)
    assert result.salutation == "use prop"


def test_hopscotch_factory() -> None:
    """The service has its own factory as a class attribute."""
    r = Registry()
    r.register_service(GreetingFactory)
    result = r.inject(GreetingFactory)
    assert result.salutation == "Hi From Factory"
