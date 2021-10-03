"""Simplest possible example."""
from dataclasses import dataclass
from hopscotch import Registry


@dataclass
class Greeter:
    """A simple greeter."""

    greeting: str = "Hello!"


registry = Registry()
registry.register(Greeter)
# Later
greeter = registry.get(Greeter)
# greeter.greeting == "Hello!"
