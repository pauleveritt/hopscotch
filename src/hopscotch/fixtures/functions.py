"""Example objects and services implemented as functions."""
from typing import Annotated
from typing import Optional

from hopscotch.fixtures import DummyOperator


def Greeting(salutation: str = "Hello") -> str:
    """A function to give a greeting."""
    return salutation


def GreetingNoDefault(salutation: str) -> str:
    """A function to give a greeting without a default."""
    return salutation


def Greeter(greeting: str) -> str:
    """A function to engage a customer."""
    return greeting


def GreeterOptional(greeting: Optional[str]) -> Optional[str]:
    """A function to engage a customer with optional greeting."""
    return greeting


def GreeterAnnotated(greeting: Annotated[str, DummyOperator("YOLO")]) -> str:
    """A function to engage a customer with an ``Annotated``."""
    return greeting


def GreeterChildren(children: tuple[str]) -> tuple[str]:
    """A function that is passed a tree of VDOM nodes."""
    return children
