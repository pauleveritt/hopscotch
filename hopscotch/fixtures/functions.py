"""Example objects and services implemented as functions."""
from typing import Optional, Annotated

from hopscotch import VDOMNode


def Greeting(salutation: str = "Hello"):
    """A function to give a greeting."""
    return salutation


def GreetingNoDefault(salutation: str):
    """A function to give a greeting without a default."""
    return salutation


def Greeter(greeting: Greeting):
    """A function to engage a customer."""
    return greeting


def GreeterOptional(greeting: Optional[Greeting]):
    """A function to engage a customer with optional greeting."""
    return greeting


def GreeterAnnotated(greeting: Annotated[Greeting, "YOLO"]):
    """A function to engage a customer with an ``Annotated``."""
    return greeting


def GreeterChildren(children: tuple[VDOMNode]):
    """A function that is passed a tree of VDOM nodes."""
    return children
