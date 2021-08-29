"""Example objects and kinds implemented as ``NamedTuple``.

Note that, since ``typing.NamedTuple`` doesn't really do inheritance,
we can't implement a ``Kind`` as a ``NamedTuple``.
"""
from typing import Annotated
from typing import NamedTuple
from typing import Optional


class Greeting(NamedTuple):
    """A ``NamedTuple`` to give a greeting."""

    salutation: str = "Hello"


class GreetingNoDefault(NamedTuple):
    """A ``NamedTuple`` to give a greeting without a default."""

    salutation: str


# Start Greeter
class Greeter(NamedTuple):
    """A ``NamedTuple`` to engage a customer."""

    greeting: Greeting


class GreeterOptional(NamedTuple):
    """A ``NamedTuple`` to engage a customer with optional greeting."""

    greeting: Optional[Greeting]


class GreeterAnnotated(NamedTuple):
    """A ``NamedTuple`` to engage a customer with an annotation."""

    greeting: Annotated[Greeting, "YOLO"]


class GreeterChildren(NamedTuple):
    """A ``NamedTuple`` that is passed a tree of VDOM nodes."""

    children: tuple[str]
