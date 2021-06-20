"""Example objects and services implemented as dataclasses."""
from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Annotated
from typing import Optional

from ..operators import Get
from ..registry import Service, Registry


@dataclass()
class Greeting:
    """A dataclass to give a greeting."""

    salutation: str = "Hello"


@dataclass()
class GreetingNoDefault:
    """A dataclass to give a greeting with no default value."""

    salutation: str


@dataclass()
class GreetingInitFalse:
    """A dataclass with a field that inits to false."""

    salutation: str = field(init=False)


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
class GreetingService(Service):
    """A dataclass ``Service`` to say greeting."""

    salutation: str = "Hello"


@dataclass()
class GreetingFactory(Service):
    """Use the ``__hopscotch_factory__`` protocol to control creation."""

    salutation: str

    @classmethod
    def __hopscotch_factory__(cls, registry: Registry) -> GreetingFactory:
        return cls(salutation="Hi From Factory")


@dataclass()
class GreetingImplementer(GreetingService):
    """A dataclass that "implements" a service."""

    salutation: str = "Hello"


@dataclass()
class Greeter:
    """A dataclass to engage a customer."""

    greeting: Greeting


@dataclass()
class GreeterService(Service):
    """A dataclass ``Service`` to engage a customer."""

    greeting: GreetingService


@dataclass()
class GreeterOptional:
    """A dataclass to engage a customer with optional greeting."""

    greeting: Optional[Greeting]


@dataclass()
class GreeterAnnotated:
    """A dataclass to engage a customer with an annotation."""

    greeting: Annotated[Greeting, "YOLO"]


@dataclass()
class GreeterChildren:
    """A dataclass that is passed a tree of VDOM nodes."""

    children: tuple[str]
