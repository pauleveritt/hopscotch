"""Register an injectable using a decorator."""
from dataclasses import dataclass
from hopscotch import injectable
from hopscotch import Registry


@injectable()
@dataclass
class Greeter:
    """A simple greeter."""

    greeting: str = "Hello!"


def main() -> str:
    """Render a template to a string."""
    registry = Registry()
    registry.scan()
    # Later
    greeter = registry.get(Greeter)
    return greeter.greeting
