"""Simplest possible example."""
from dataclasses import dataclass

from hopscotch import Registry


@dataclass
class Greeter:
    """A simple greeter."""

    greeting: str = "Hello!"


def main() -> str:
    """Render a template to a string."""
    registry = Registry()
    registry.register(Greeter)
    # Later
    greeter = registry.get(Greeter)
    return greeter.greeting
