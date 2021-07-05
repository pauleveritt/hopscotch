"""Test the registry implementation and helpers."""
from dataclasses import dataclass
from typing import Optional

import pytest

from hopscotch.fixtures.dataklasses import Greeting, Customer, FrenchCustomer
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


def test_singleton_registry_context_none() -> None:
    """When registry context is none, get correct singletons."""
    greeting = Greeting(salutation="no context")
    customer_greeting = Greeting(salutation="customer")

    # ### A bunch of single-registration cases, no precedence involved
    # Singleton with context=None
    r = Registry(context=None)
    r.register_singleton(greeting)
    assert r.get_service(Greeting).salutation == "no context"
    # Singleton with context=Customer
    r = Registry(context=None)
    r.register_singleton(customer_greeting, context=Customer)
    with pytest.raises(LookupError):
        r.get_service(Greeting)


def test_singleton_registry_context_customer() -> None:
    """When registry context is ``Customer``, get correct singletons."""

    @dataclass()
    class NonCustomer:
        salutation: str = "Not a Customer"

    customer = Customer(first_name="customer")
    greeting = Greeting(salutation="no context")
    customer_greeting = Greeting(salutation="customer")
    french_greeting = Greeting(salutation="french customer")
    non_customer_greeting = Greeting(salutation="non customer")

    # ### A bunch of single-registration cases, no precedence involved
    # singleton.context=None
    r = Registry(context=customer)
    r.register_singleton(greeting)
    assert r.get_service(Greeting).salutation == "no context"

    # singleton.context=Customer means match
    r = Registry(context=customer)
    r.register_singleton(customer_greeting, context=Customer)
    assert r.get_service(Greeting).salutation == "customer"

    # singleton.context=FrenchCustomer means *no* match, too specific
    r = Registry(context=customer)
    r.register_singleton(french_greeting, context=FrenchCustomer)
    with pytest.raises(LookupError):
        r.get_service(Greeting)

    # singleton.context=NonCustomer means *no* match, not same type.
    r = Registry(context=customer)
    r.register_singleton(non_customer_greeting, context=NonCustomer)
    with pytest.raises(LookupError):
        r.get_service(Greeting)


def test_singleton_registry_context_french_customer() -> None:
    """When registry context is ``FrenchCustomer``, get correct singletons."""

    @dataclass()
    class NonCustomer:
        salutation: str = "Not a Customer"

    french_customer = FrenchCustomer(first_name="french customer")
    greeting = Greeting(salutation="no context")
    customer_greeting = Greeting(salutation="customer")
    french_greeting = Greeting(salutation="french customer")
    non_customer_greeting = Greeting(salutation="non customer")

    # ### A bunch of single-registration cases, no precedence involved
    # singleton.context=None
    r = Registry(context=french_customer)
    r.register_singleton(greeting)
    assert r.get_service(Greeting).salutation == "no context"

    # singleton.context=Customer means match
    r = Registry(context=french_customer)
    r.register_singleton(customer_greeting, context=Customer)
    assert r.get_service(Greeting).salutation == "customer"

    # singleton.context=FrenchCustomer matches
    r = Registry(context=french_customer)
    r.register_singleton(french_greeting, context=FrenchCustomer)
    assert r.get_service(Greeting).salutation == "french customer"

    # singleton.context=NonCustomer means *no* match, not same type.
    r = Registry(context=french_customer)
    r.register_singleton(non_customer_greeting, context=NonCustomer)
    with pytest.raises(LookupError):
        r.get_service(Greeting)


def test_singleton_registry_context_french_multiple() -> None:
    """Registry context is ``FrenchCustomer``, get singletons from multiple."""

    @dataclass()
    class NonCustomer:
        salutation: str = "Not a Customer"

    customer = Customer(first_name="customer")
    french_customer = FrenchCustomer(first_name="french customer")
    greeting = Greeting(salutation="no context")
    customer_greeting = Greeting(salutation="customer")
    french_greeting = Greeting(salutation="french customer")
    non_customer_greeting = Greeting(salutation="non customer")

    # ### A bunch of multiple-registration cases, no precedence involved
    # No context on registrations, choose last one.
    r = Registry(context=french_customer)
    r.register_singleton(greeting)
    r.register_singleton(Greeting(salutation="second"))
    assert r.get_service(Greeting).salutation == "second"

    # Matching the exact class is highest precedence
    r = Registry(context=french_customer)
    r.register_singleton(greeting)
    r.register_singleton(french_greeting, context=FrenchCustomer)
    r.register_singleton(customer_greeting, context=Customer)
    assert r.get_service(Greeting).salutation == "french customer"

    # Matching the exact class is highest precedence, registration order
    # doesn't matter
    r = Registry(context=french_customer)
    r.register_singleton(french_greeting, context=FrenchCustomer)
    r.register_singleton(greeting)
    r.register_singleton(customer_greeting, context=Customer)
    assert r.get_service(Greeting).salutation == "french customer"

    # Matching a subclass is highest precedence
    r = Registry(context=french_customer)
    r.register_singleton(greeting)
    r.register_singleton(customer_greeting, context=Customer)
    assert r.get_service(Greeting).salutation == "customer"

    # Matching the class is higher precedence, registration order
    # doesn't matter.
    r = Registry(context=french_customer)
    r.register_singleton(customer_greeting, context=Customer)
    r.register_singleton(greeting)
    assert r.get_service(Greeting).salutation == "customer"

    # Adding in a type that doesn't subclass, doesn't matter.
    r = Registry(context=french_customer)
    r.register_singleton(customer_greeting, context=Customer)
    r.register_singleton(non_customer_greeting, context=NonCustomer)
    r.register_singleton(greeting)
    assert r.get_service(Greeting).salutation == "customer"


def test_get_singleton() -> None:
    """Return a singleton that has no service it is registered against."""
    registry = Registry()
    greeting = Greeting()
    registry.register_singleton(greeting)
    result = registry.get_service(Greeting)
    assert greeting is result


def test_get_singleton_service() -> None:
    """Return a singleton that is registered against a service."""
    registry = Registry()
    greeting = GreetingImplementer()
    registry.register_singleton(greeting, servicetype=GreetingService)
    result = registry.get_service(GreetingService)
    assert greeting.salutation == result.salutation


def test_get_singleton_service_subclass() -> None:
    """Return a singleton that subclasses a service."""
    registry = Registry()
    greeting = GreetingImplementer()
    registry.register_singleton(greeting, servicetype=GreetingService)
    result = registry.get_service(GreetingService)
    assert greeting is result


def test_get_services_found_class() -> None:
    """Construct an instance from a matching class."""
    registry = Registry()
    greeting = GreetingImplementer()

    # Let's override the registry method with a dummy
    def fake_instantiate_class(cls: object, props: object) -> object:
        return greeting

    setattr(registry, "instantiate_service", fake_instantiate_class)
    registry.classes[GreetingService] = [
        GreetingImplementer,
    ]
    result = registry.get_service(GreetingService)
    assert greeting == result


def test_get_services_match_in_parent() -> None:
    """No local match but is found in parent."""
    parent_registry = Registry()
    greeting = GreetingImplementer()
    setattr(parent_registry, "instantiate_service", lambda x: greeting)
    parent_registry.classes[GreetingService] = [
        GreetingImplementer,
    ]

    # Make a child registry which has nothing registered
    child_registry = Registry(parent=parent_registry)
    result = child_registry.get_service(GreetingService)
    assert greeting == result


def test_register_singleton_with_class() -> None:
    """Register a singleton with the longer format."""
    registry = Registry()
    greeting = Greeting()
    registry.register_singleton(greeting)
    assert greeting == registry.singletons[Greeting]
    registration = registry.registrations[Greeting][0]
    assert registration.is_singleton
    assert registration.implementation == greeting
    assert registration.servicetype is None


def test_register_singleton_without_class() -> None:
    """Register a singleton with the shorter format."""
    registry = Registry()
    greeting = GreetingImplementer()
    registry.register_singleton(greeting)
    assert greeting == registry.singletons[GreetingImplementer]


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
    registration = Registration(
        implementation=Greeting,
        context=Greeting,
    )
    assert registration.implementation is Greeting
    assert registration.servicetype is None
    assert registration.context is Greeting
    assert registration.field_infos == []
    assert not registration.is_singleton


def test_registration_with_servicetype() -> None:
    """Ensure a registration can be created with a servicetype."""
    registration = Registration(
        implementation=GreetingImplementer,
        servicetype=GreetingService,
        context=Greeting,
    )
    assert registration.implementation is GreetingImplementer
    assert registration.servicetype is GreetingService
    assert registration.context is Greeting
    assert registration.field_infos == []


def test_registration_singleton() -> None:
    """Ensure a singleton registration."""
    registration = Registration(
        implementation=Greeting,
        is_singleton=True,
    )
    assert registration.is_singleton


def test_registration_with_no_context() -> None:
    """Ensure a registration can be created without a context."""
    registration = Registration(implementation=Greeting)
    assert registration.implementation is Greeting
    assert registration.servicetype is None
    assert registration.context is None
    assert registration.field_infos == []


def test_context_registration_no_context() -> None:
    """A registration for a context in a registry with none."""
    registry = Registry()
    registry.register_service(GreetingService, context=Customer)
    registry.get_service(GreetingService)

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
