"""Example objects and services implemented as dataclasses."""
from dataclasses import dataclass
from typing import Annotated, Optional

from . import Service


@dataclass()
class Greeting:
    """A dataclass to give a greeting."""

    salutation: str = "Hello"


@dataclass()
class GreetingNoDefault:
    """A dataclass to give a greeting with no default value."""

    salutation: str


@dataclass()
class GreetingService(Service):
    """A dataclass ``Service`` to say greeting."""

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
    """A dataclass  to engage a customer with optional greeting."""

    greeting: Optional[Greeting]


@dataclass()
class GreeterAnnotated:
    """A plain-old-class to engage a customer with an annotation."""

    greeting: Annotated[Greeting, "YOLO"]

    def __init__(self, greeting: Greeting):
        """Construct a greeter that uses Annotated."""
        self.greeting = greeting
