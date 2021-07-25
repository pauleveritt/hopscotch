"""Test the registry implementation and helpers."""
from dataclasses import dataclass
from typing import Optional

import pytest

from hopscotch.fixtures.dataklasses import Greeting, Customer, FrenchCustomer
from hopscotch.fixtures.dataklasses import AnotherGreeting
from hopscotch.registry import Registry, Registration


class DummyScan:
    """Mock out the venusian scanner."""

    def __init__(self):  # type: ignore
        """Fake called_with for use later."""
        self.called_with: Optional[object] = None

    def __call__(self, pkg: Optional[object]) -> None:
        """Set the called_with to simulate the caller."""
        self.called_with = pkg


def test_singleton_registry_context_none() -> None:
    """When registry context is none, get correct singletons."""
    greeting = Greeting(salutation="no context")
    customer_greeting = Greeting(salutation="customer")

    # Singleton with context=None
    r = Registry(context=None)
    r.register(greeting)
    assert r.get(Greeting).salutation == "no context"
    # Singleton with context=Customer
    r = Registry(context=None)
    r.register(customer_greeting, context=Customer)
    with pytest.raises(LookupError):
        r.get(Greeting)


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
    r.register(greeting)
    assert r.get(Greeting).salutation == "no context"

    # singleton.context=Customer means match
    r = Registry(context=customer)
    r.register(customer_greeting, context=Customer)
    assert r.get(Greeting).salutation == "customer"

    # singleton.context=FrenchCustomer means *no* match, too specific
    r = Registry(context=customer)
    r.register(french_greeting, context=FrenchCustomer)
    with pytest.raises(LookupError):
        r.get(Greeting)

    # singleton.context=NonCustomer means *no* match, not same type.
    r = Registry(context=customer)
    r.register(non_customer_greeting, context=NonCustomer)
    with pytest.raises(LookupError):
        r.get(Greeting)


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
    r.register(greeting)
    assert r.get(Greeting).salutation == "no context"

    # singleton.context=Customer means match
    r = Registry(context=french_customer)
    r.register(customer_greeting, context=Customer)
    assert r.get(Greeting).salutation == "customer"

    # singleton.context=FrenchCustomer matches
    r = Registry(context=french_customer)
    r.register(french_greeting, context=FrenchCustomer)
    assert r.get(Greeting).salutation == "french customer"

    # singleton.context=NonCustomer means *no* match, not same type.
    r = Registry(context=french_customer)
    r.register(non_customer_greeting, context=NonCustomer)
    with pytest.raises(LookupError):
        r.get(Greeting)


def test_singleton_registry_context_french_multiple() -> None:
    """Registry context is ``FrenchCustomer``, get singletons from multiple."""

    @dataclass()
    class NonCustomer:
        salutation: str = "Not a Customer"

    french_customer = FrenchCustomer(first_name="french customer")
    greeting = Greeting(salutation="no context")
    customer_greeting = Greeting(salutation="customer")
    french_greeting = Greeting(salutation="french customer")
    non_customer_greeting = Greeting(salutation="non customer")

    # ### A bunch of multiple-registration cases, no precedence involved
    # No context on registrations, choose last one.
    r = Registry(context=french_customer)
    r.register(greeting)
    r.register(Greeting(salutation="second"))
    assert r.get(Greeting).salutation == "second"

    # Matching the exact class is highest precedence
    r = Registry(context=french_customer)
    r.register(greeting)
    r.register(french_greeting, context=FrenchCustomer)
    r.register(customer_greeting, context=Customer)
    assert r.get(Greeting).salutation == "french customer"

    # Matching the exact class is highest precedence, registration order
    # doesn't matter
    r = Registry(context=french_customer)
    r.register(french_greeting, context=FrenchCustomer)
    r.register(greeting)
    r.register(customer_greeting, context=Customer)
    assert r.get(Greeting).salutation == "french customer"

    # Matching a subclass is highest precedence
    r = Registry(context=french_customer)
    r.register(greeting)
    r.register(customer_greeting, context=Customer)
    assert r.get(Greeting).salutation == "customer"

    # Matching the class is higher precedence, registration order
    # doesn't matter.
    r = Registry(context=french_customer)
    r.register(customer_greeting, context=Customer)
    r.register(greeting)
    assert r.get(Greeting).salutation == "customer"

    # Adding in a type that doesn't subclass, doesn't matter.
    r = Registry(context=french_customer)
    r.register(customer_greeting, context=Customer)
    r.register(non_customer_greeting, context=NonCustomer)
    r.register(greeting)
    assert r.get(Greeting).salutation == "customer"


def test_get_singleton() -> None:
    """Return a singleton that has no service it is registered against."""
    registry = Registry()
    greeting = Greeting()
    registry.register(greeting)
    result = registry.get(Greeting)
    assert greeting is result


def test_get_singleton_service() -> None:
    """Return a singleton that is registered against a service."""
    registry = Registry()
    greeting = AnotherGreeting()
    registry.register(greeting, servicetype=Greeting)
    result = registry.get(Greeting)
    assert greeting.salutation == result.salutation


def test_get_singleton_service_subclass() -> None:
    """Return a singleton that subclasses a service."""
    registry = Registry()
    greeting = AnotherGreeting()
    registry.register(greeting, servicetype=Greeting)
    result = registry.get(Greeting)
    assert greeting is result


def test_get_services_found_class() -> None:
    """Construct an instance from a matching class."""
    registry = Registry()
    greeting = AnotherGreeting()
    registry.register(AnotherGreeting, servicetype=Greeting)
    result = registry.get(Greeting)
    assert greeting == result


def test_get_services_match_in_parent() -> None:
    """No local match but is found in parent."""
    parent_registry = Registry()
    greeting = AnotherGreeting()
    parent_registry.register(AnotherGreeting, servicetype=Greeting)

    # Make a child registry which has nothing registered
    child_registry = Registry(parent=parent_registry)
    result = child_registry.get(Greeting)
    assert greeting == result


def test_register_service_with_class() -> None:
    """Register a singleton with the longer format."""
    registry = Registry()
    greeting = Greeting()
    registry.register(greeting)
    greetings = registry.registrations[Greeting]
    registration = greetings["singletons"][None][0]
    assert registration.is_singleton
    assert registration.implementation == greeting
    assert registration.servicetype is None


def test_register_service_without_class() -> None:
    """Register a singleton with the shorter format."""
    registry = Registry()
    greeting = AnotherGreeting()
    registry.register(greeting)
    gi = registry.registrations[AnotherGreeting]
    first = gi["singletons"][None][0]
    assert first.implementation == greeting
    assert first.is_singleton


def test_register_class() -> None:
    """Register a class then ensure it is present."""
    registry = Registry()
    registry.register(AnotherGreeting, servicetype=Greeting)
    registrations = registry.registrations[Greeting]["classes"][None]
    registration = registrations[0]
    assert AnotherGreeting is registration.implementation
    gs = registry.registrations[Greeting]
    first = gs["classes"][None][0]
    assert first.implementation is AnotherGreeting
    assert first.servicetype is Greeting
    assert not first.is_singleton


def test_register_class_with_context() -> None:
    """Register a class for a context then ensure it is present."""
    registry = Registry()
    registry.register(
        AnotherGreeting, servicetype=Greeting, context=FrenchCustomer
    )
    classes = registry.registrations[Greeting]["classes"]
    registrations = classes[FrenchCustomer]
    registration = registrations[0]
    assert AnotherGreeting == registration.implementation
    gs = registry.registrations[Greeting]
    assert gs["classes"][None] == []
    first = gs["classes"][FrenchCustomer][0]
    assert first.implementation is AnotherGreeting
    assert first.servicetype is Greeting
    assert not first.is_singleton


def test_get_last_singleton_registration() -> None:
    """Register multiple singletons, last one wins."""
    g1 = Greeting(salutation="G1")
    g2 = Greeting(salutation="G2")
    registry = Registry()
    registry.register(g1)
    registry.register(g2)
    result = registry.get(Greeting)
    assert "G2" == result.salutation


def test_get_last_class_registration() -> None:
    """Register multiple classes, last one wins."""

    @dataclass()
    class GreetingImplementer2(Greeting):
        salutation: str = "G2"

    registry = Registry()
    registry.register(AnotherGreeting, servicetype=Greeting)
    registry.register(GreetingImplementer2, servicetype=Greeting)
    result = registry.get(Greeting)
    assert "G2" == result.salutation


def test_parent_registry() -> None:
    """Match a registry in the parent registry."""

    @dataclass()
    class GreetingImplementer2(Greeting):
        salutation: str = "G2"

    parent_registry = Registry()
    parent_registry.register(AnotherGreeting, servicetype=Greeting)
    child_registry = Registry(parent=parent_registry)
    child_registry.register(GreetingImplementer2, servicetype=Greeting)
    result = child_registry.get(Greeting)
    assert result.salutation == "G2"


def test_child_registry() -> None:
    """Match a registry in the child registry."""

    @dataclass()
    class GreetingImplementer2(Greeting):
        salutation: str = "G2"

    parent_registry = Registry()
    parent_registry.register(AnotherGreeting, servicetype=Greeting)
    parent_registry.register(GreetingImplementer2, servicetype=Greeting)
    child_registry = Registry(parent=parent_registry)
    result = child_registry.get(Greeting)
    assert "G2" == result.salutation


def test_injector_registry_scan_caller() -> None:
    """Pretend to scan and see if called_with is set correctly."""
    registry = Registry()
    ds = DummyScan()  # type: ignore
    registry.scanner.scan = ds
    registry.scan()
    assert "tests" == ds.called_with.__name__  # type: ignore


def test_registration_with_context() -> None:
    """Ensure a registration can be created with a context."""
    registration = Registration(
        implementation=Greeting,
        context=Greeting,
    )
    assert registration.implementation is Greeting
    assert registration.servicetype is None
    assert registration.context is Greeting
    assert len(registration.field_infos) == 1
    assert not registration.is_singleton


def test_registration_with_servicetype() -> None:
    """Ensure a registration can be created with a servicetype."""
    registration = Registration(
        implementation=AnotherGreeting,
        servicetype=Greeting,
        context=Greeting,
    )
    assert registration.implementation is AnotherGreeting
    assert registration.servicetype is Greeting
    assert registration.context is Greeting
    assert len(registration.field_infos) == 1


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
    assert len(registration.field_infos) == 1


def test_context_registration_no_context() -> None:
    """A registration for a context in a registry with none."""
    registry = Registry()
    registry.register(Greeting, context=Customer)
    with pytest.raises(LookupError):
        registry.get(Greeting)

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