"""Replace a built-in class."""
from dataclasses import dataclass

from hopscotch import injectable
from hopscotch import Registry


@dataclass
class Customer:
    """A basic customer."""

    name: str = "Mary"


@dataclass
class FrenchCustomer:
    """A different customer."""

    name: str = "Marie"


@injectable()
@dataclass
class Greeter:
    """A simple greeter."""

    greeting: str = "Hello!"


# Some site might want to change a built-in.
@injectable(kind=Greeter, context=FrenchCustomer)
@dataclass
class FrenchGreeter:
    """Provide a different ``Greeter`` in this site."""

    greeting: str = "Bonjour!"


def main() -> tuple[str, str]:
    """Render a template to a string."""
    customer = Customer()
    french_customer = FrenchCustomer()
    parent_registry = Registry(context=customer)
    parent_registry.scan()
    # Later
    greeter1 = parent_registry.get(Greeter)

    # Much later
    child_registry = Registry(parent=parent_registry, context=french_customer)
    greeter2 = child_registry.get(Greeter)

    return greeter1.greeting, greeter2.greeting
