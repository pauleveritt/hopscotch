"""Example objects and services implemented as plain classes."""
from typing import Annotated
from typing import Optional

from . import Service
from .. import VDOMNode


class Greeting:
    """A plain-old-class to give a greeting."""

    salutation: str = "Hello"


class GreetingNoDefault:
    """A plain-old-class to give a greeting without a default."""

    salutation: str = "Hello"

    def __init__(self, salutation: str):
        """Store salutation on the instance."""
        self.salutation = salutation


class GreetingService(Service):
    """A plain-old-class ``Service`` to say greeting."""

    salutation: str = "Hello"


class Greeter:
    """A plain-old-class to engage a customer."""

    greeting: Greeting

    def __init__(self, greeting: Greeting):
        """Construct a greeter."""
        self.greeting = greeting


class GreeterService(Service):
    """A plain-old-class ``Service`` to engage a customer."""

    greeting: GreetingService

    def __init__(self, greeting: GreetingService):
        """Construct a greeter that is a service."""
        self.greeting = greeting


class GreeterOptional:
    """A plain-old-class to engage a customer with optional greeting."""

    greeting: Optional[Greeting]

    def __init__(self, greeting: Optional[Greeting]):
        """Construct a greeter with an optional greeting."""
        self.greeting = greeting


class GreeterAnnotated:
    """A plain-old-class to engage a customer with an annotation."""

    greeting: Annotated[Greeting, "YOLO"]

    def __init__(self, greeting: Greeting):
        """Construct a greeter that uses Annotated."""
        self.greeting = greeting


class GreeterChildren:
    """A plain-old-class that is passed a tree of VDOM nodes."""

    children: tuple[VDOMNode]

    def __init__(self, children: tuple[VDOMNode]):
        """Construct a greeter that has children."""
        self.children = children
