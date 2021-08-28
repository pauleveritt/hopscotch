"""Register with a decorator."""
from dataclasses import dataclass

from hopscotch import Registry, injectable


@injectable()
@dataclass
class Greeter:
    """A simple greeter."""

    greeting: str = "Hello!"


registry = Registry()
registry.scan()
# Later
greeter = registry.get(Greeter)
# greeter.greeting == "Hello!"
