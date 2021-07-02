"""Test the registry implementation and helpers."""
from dataclasses import dataclass
from typing import Optional

import pytest

from hopscotch.fixtures.dataklasses import Greeting
from hopscotch.fixtures.dataklasses import GreetingImplementer
from hopscotch.fixtures.dataklasses import GreetingService
from hopscotch.registry import Registry, is_service_component, Registration


class DummyScan:
    """Mock out the venusian scanner."""

    def __init__(self):  # type: ignore
        """Fake called_with for use later."""
        self.called_with: Optional[object] = None

    def __call__(self, pkg: Optional[object]) -> None:
        """Set the called_with to simulate the caller."""
        self.called_with = pkg


def test_construction() -> None:
    """Ensure the registry is setup correctly."""
    registry = Registry()
    assert {} == registry.classes
    assert {} == registry.service_infos


def test_get_singleton() -> None:
    """Return a singleton that has no service it is registered against."""
    registry = Registry()
    di = Greeting()
    registry.register_singleton(di)
    result = registry.get_service(Greeting)
    assert di is result


def test_get_singleton_service() -> None:
    """Return a singleton that is registered against a service."""
    registry = Registry()
    di = GreetingImplementer()
    registry.register_singleton(di, servicetype=GreetingService)
    result = registry.get_service(GreetingService)
    assert di.salutation == result.salutation


def test_get_singleton_service_subclass() -> None:
    """Return a singleton that subclasses a service."""
    registry = Registry()
    di = GreetingImplementer()
    registry.register_singleton(di, servicetype=GreetingService)
    result = registry.get_service(GreetingService)
    assert di is result


def test_get_services_found_class() -> None:
    """Construct an instance from a matching class."""
    registry = Registry()
    di = GreetingImplementer()

    # Let's override the registry method with a dummy
    def fake_instantiate_class(cls: object, props: object) -> object:
        return di

    setattr(registry, "instantiate_service", fake_instantiate_class)
    registry.classes[GreetingService] = [
        GreetingImplementer,
    ]
    result = registry.get_service(GreetingService)
    assert di == result


def test_get_services_match_in_parent() -> None:
    """No local match but is found in parent."""
    parent_registry = Registry()
    di = GreetingImplementer()
    setattr(parent_registry, "instantiate_service", lambda x: di)
    parent_registry.classes[GreetingService] = [
        GreetingImplementer,
    ]

    # Make a child registry which has nothing registered
    child_registry = Registry(parent=parent_registry)
    result = child_registry.get_service(GreetingService)
    assert di == result


def test_register_singleton_with_class() -> None:
    """Register a singleton with the longer format."""
    registry = Registry()
    di = GreetingImplementer()
    registry.register_singleton(di)
    assert di == registry.singletons[GreetingImplementer]


def test_register_singleton_without_class() -> None:
    """Register a singleton with the shorter format."""
    registry = Registry()
    di = GreetingImplementer()
    registry.register_singleton(di)
    assert di == registry.singletons[GreetingImplementer]


def test_register_class() -> None:
    """Register a class then ensure it is present."""
    registry = Registry()
    registry.register_service(GreetingImplementer, servicetype=GreetingService)
    assert [GreetingImplementer] == registry.classes[GreetingService]


def test_get_last_singleton_registration() -> None:
    """Register multiple singletons, last one wins."""
    g1 = Greeting(salutation="G1")
    g2 = Greeting(salutation="G2")
    registry = Registry()
    registry.register_singleton(g1)
    registry.register_singleton(g2)
    result = registry.get_service(Greeting)
    assert "G2" == result.salutation


def test_get_last_class_registration() -> None:
    """Register multiple classes, last one wins."""

    @dataclass()
    class GreetingImplementer2(GreetingService):
        salutation: str = "G2"

    registry = Registry()
    registry.register_service(GreetingImplementer, servicetype=GreetingService)
    registry.register_service(GreetingImplementer2, servicetype=GreetingService)
    result = registry.get_service(GreetingService)
    assert "G2" == result.salutation


def test_parent_registry() -> None:
    """Match a registry in the parent registry."""

    @dataclass()
    class GreetingImplementer2(GreetingService):
        salutation: str = "G2"

    parent_registry = Registry()
    parent_registry.register_service(GreetingImplementer, servicetype=GreetingService)
    child_registry = Registry(parent=parent_registry)
    child_registry.register_service(GreetingImplementer2, servicetype=GreetingService)
    result = child_registry.get_service(GreetingService)
    assert result.salutation == "G2"


def test_child_registry() -> None:
    """Match a registry in the child registry."""

    @dataclass()
    class GreetingImplementer2(GreetingService):
        salutation: str = "G2"

    parent_registry = Registry()
    parent_registry.register_service(GreetingImplementer, servicetype=GreetingService)
    parent_registry.register_service(GreetingImplementer2, servicetype=GreetingService)
    child_registry = Registry(parent=parent_registry)
    result = child_registry.get_service(GreetingService)
    assert "G2" == result.salutation


def test_get_implementations_match() -> None:
    """Find the implementations in a flat registry."""
    registry = Registry()
    registry.register_service(Greeting)
    first_result = registry.get_implementations(Greeting)[0]
    assert first_result.salutation == "Hello"


def test_get_nested_implementations_match() -> None:
    """Find the implementations in a nested registry."""
    parent_registry = Registry()
    parent_registry.register_service(Greeting)
    child_registry = Registry(parent=parent_registry)
    first_result = child_registry.get_implementations(Greeting)[0]
    assert first_result.salutation == "Hello"


def test_get_implementations_no_match() -> None:
    """No match should result in ``LookupError``."""
    registry = Registry()
    with pytest.raises(LookupError) as exc:
        registry.get_implementations(Greeting)
    assert "No service 'Greeting' in registry" == exc.value.args[0]


def test_get_nested_implementations_no_match() -> None:
    """No match should result in ``LookupError``."""
    parent_registry = Registry()
    child_registry = Registry(parent=parent_registry)
    with pytest.raises(LookupError) as exc:
        child_registry.get_implementations(Greeting)
    assert "No service 'Greeting' in registry" == exc.value.args[0]


def test_injector_registry_scan_caller() -> None:
    """Pretend to scan and see if called_with is set correctly."""
    registry = Registry()
    ds = DummyScan()  # type: ignore
    registry.scanner.scan = ds
    registry.scan()
    assert "tests" == ds.called_with.__name__  # type: ignore


def test_is_service_component() -> None:
    """Check if the helper does return true for a subclass."""
    assert is_service_component(GreetingService)


def test_is_not_service_component() -> None:
    """Check if the helper returns false for a non-class."""
    assert not is_service_component(999)


def test_get_service_info() -> None:
    """Get the cached value of service info, starting at first time."""

    registry = Registry()
    assert GreetingService not in registry.service_infos
    # Register GreetingService and show it isn't there yet
    registry.register_service(GreetingService)
    assert GreetingService not in registry.service_infos
    service_info = registry.get_service_info(GreetingService)
    assert GreetingService in registry.service_infos
    assert service_info.field_infos[0].field_name == "salutation"


def test_registration_with_context() -> None:
    """Ensure a registration can be created with a context."""
    registration = Registration(context=Greeting)
    assert registration.context is Greeting
    assert registration.field_infos == []


def test_registration_with_no_context() -> None:
    """Ensure a registration can be created without a context."""
    registration = Registration()
    assert registration.context is None
    assert registration.field_infos == []

# FIXME Bring this back when examples are back
# def test_injector_registry_scan_pkg():
#     from examples import d_decorators
#
#     registry = Registry()
#     ds = DummyScan()
#     registry.scanner.scan = ds
#     registry.scan(d_decorators)
#     if ds.called_with:
#         assert "examples.d_decorators" == ds.called_with.__name__


# def test_injector_registry_scan_string():
#     registry = Registry()
#     ds = DummyScan()
#     registry.scanner.scan = ds
#     registry.scan("examples.d_decorators")
#     assert "examples.d_decorators" == ds.called_with.__name__  # type: ignore
