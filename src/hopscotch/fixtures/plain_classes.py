"""Example objects and kinds implemented as plain classes."""
from typing import Annotated
from typing import Optional


class Greeting:
    """A plain-old-class to give a greeting."""

    salutation: str = "Hello"


class GreetingNoDefault:
    """A plain-old-class to give a greeting without a default."""

    salutation: str = "Hello"

    def __init__(self, salutation: str):
        """Store salutation on the instance."""
        self.salutation = salutation


# Start Greeter
class Greeter:
    """A plain-old-class to engage a customer."""

    greeting: Greeting

    def __init__(self, greeting: Greeting):
        """Construct a greeter."""
        self.greeting = greeting


class GreeterKind:
    """A plain-old-class ``Kind`` to engage a customer."""

    greeting: Greeting

    def __init__(self, greeting: Greeting):
        """Construct a greeter that is a kind."""
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

    children: tuple[str]

    def __init__(self, children: tuple[str]):
        """Construct a greeter that has children."""
        self.children = children
