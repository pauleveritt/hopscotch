"""Example objects and kinds implemented as functions."""
from typing import Annotated
from typing import Optional

from hopscotch.fixtures.dataklasses import Customer
from hopscotch.operators import Get


def Greeting(salutation: str = "Hello") -> str:
    """A function to give a greeting."""
    return salutation


def GreetingDefaultNoHint(salutation="Hello") -> str:  # type: ignore
    """A function to with a parameter having no hint."""
    return salutation  # type: ignore


def GreetingNoDefault(salutation: str) -> str:
    """A function to give a greeting without a default."""
    return salutation


# Start Greeter
def Greeter(greeting: str) -> str:
    """A function to engage a customer."""
    return greeting


# Start GreeterOptional
def GreeterOptional(greeting: Optional[str]) -> Optional[str]:
    """A function to engage a customer with optional greeting."""
    return greeting


# Start GreeterAnnotated
def GreeterAnnotated(
    customer_name: Annotated[str, Get(Customer, attr="first_name")]
) -> str:
    """A function to engage a customer with an ``Annotated``."""
    return customer_name


def GreeterChildren(children: tuple[str]) -> tuple[str]:
    """A function that is passed a tree of VDOM nodes."""
    return children
