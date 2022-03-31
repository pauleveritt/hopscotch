"""Replace a built-in class."""
from dataclasses import dataclass

from hopscotch import injectable
from hopscotch import Registry


@dataclass
class Greeter:
    """A simple greeter."""

    greeting: str = "Hello!"


# Some site might want to change a built-in.
@injectable(kind=Greeter)
@dataclass
class CustomGreeter:
    """Provide a different ``Greeter`` in this site."""

    greeting: str = "Howdy!"


def main() -> str:
    """Render a template to a string."""
    # Make app and register built-ins
    registry = Registry()
    registry.register(Greeter)
    # Still during startup, but later during site registration
    registry.scan()
    # Later, when processing a request
    greeter = registry.get(Greeter)
    return greeter.greeting
