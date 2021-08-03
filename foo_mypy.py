from dataclasses import dataclass
from typing import TypeVar, Type


@dataclass()
class Greeting:
    """A dataclass to give a greeting."""

    salutation: str = "Hello"

@dataclass()
class AnotherGreeting(Greeting):
    """A dataclass to give a greeting."""

    salutation: str = "Another"


T = TypeVar("T")


def get_thing(implementation: T, servicetype: Type[T]) -> T:
    return implementation


get_thing(AnotherGreeting, servicetype=Greeting)
