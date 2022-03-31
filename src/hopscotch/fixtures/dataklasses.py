"""Example objects and kinds implemented as dataclasses."""
from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Annotated
from typing import Optional

from hopscotch import injectable
from hopscotch import Registry
from hopscotch.operators import Context
from hopscotch.operators import context
from hopscotch.operators import Get
from hopscotch.operators import get


# Decorate Greeting
@injectable()
@dataclass()  # Start Greeting
class Greeting:
    """A dataclass to give a greeting."""

    salutation: str = "Hello"


# Start AnotherGreeting
@dataclass()
class AnotherGreeting(Greeting):
    """A replacement alternative for the default ``Greeting``."""

    salutation: str = "Another Hello"


@dataclass()
class GreetingNoDefault:
    """A dataclass to give a greeting with no default value."""

    salutation: str


@dataclass()
class GreetingInitFalse:
    """A dataclass with a field that inits to false."""

    salutation: str = field(init=False)


@dataclass()
class GreetingFieldDefault:
    """A dataclass with a field using a default argument."""

    salutation: str = field(default="Default Argument")


@dataclass()
class GreetingFieldDefaultFactory:
    """A dataclass with a field using a default factory."""

    salutation: list = field(default_factory=list)


@dataclass()
class GreetingOperator:
    """A dataclass to give a greeting via an operator."""

    greeter: Annotated[
        Greeting,
        Get(Greeting),
    ]


@dataclass()
class GreetingTuple:
    """A dataclass to give a sequence of greetings."""

    salutation: tuple[str, ...]


@dataclass()
class GreetingPath:
    """A dataclass to give a builtin Path."""

    location: Path


# Start GreetingFactory
@dataclass()
class GreetingFactory:
    """Use the ``__hopscotch_factory__`` protocol to control creation."""

    salutation: str

    @classmethod
    def __hopscotch_factory__(cls, registry: Registry) -> GreetingFactory:
        """Manually construct this instance, instead of injection."""
        return cls(salutation="Hi From Factory")


# Start Greeter
@injectable()
@dataclass()
class Greeter:
    """A dataclass to engage a customer."""

    greeting: Greeting


# Start GreeterKind
@dataclass()
class GreeterKind:
    """A dataclass ``Kind`` to engage a customer."""

    greeting: Greeting


# Start GreeterOptional
@dataclass()
class GreeterOptional:
    """A dataclass to engage a customer with optional greeting."""

    greeting: Optional[Greeting]  # no default


@dataclass()
class GreeterAnnotated:
    """A dataclass to engage a customer with an annotation."""

    greeting: Annotated[Greeting, "YOLO"]


@dataclass()
class GreeterChildren:
    """A dataclass that is passed a tree of VDOM nodes."""

    children: tuple[str]


@dataclass()
class GreeterRegistry:
    """A dataclass that depends on the registry."""

    registry: Registry


# Start Customer
@dataclass()
class Customer:
    """The person to greet, stored as the registry context."""

    first_name: str


@dataclass()
class FrenchCustomer(Customer):
    """A different kind of person to greet, stored as the registry context."""

    first_name: str


@injectable()
@dataclass()
class GreeterCustomer:
    """A dataclass that depends on the registry context."""

    customer: Annotated[Customer, Context()]


# Start GreeterFrenchCustomer
@injectable(context=FrenchCustomer)
@dataclass()
class GreeterFrenchCustomer:
    """A dataclass that depends on a different registry context."""

    customer: FrenchCustomer = context()


# Start GreeterGetAnother
@injectable()
@dataclass()
class GreeterGetAnother:
    """Use an operator to change the type hint of what's retrieved."""

    customer_name: AnotherGreeting = get(Greeting)


# Start GreeterFirstName
@dataclass()
class GreeterFirstName:
    """A dataclass that gets an attribute off a dependency."""

    customer_name: str = get(Customer, attr="first_name")
