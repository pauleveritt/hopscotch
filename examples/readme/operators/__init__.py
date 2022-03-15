"""Rich dependency injection with operators."""
from dataclasses import dataclass
from hopscotch import injectable
from hopscotch import Registry
from hopscotch.operators import get


@injectable()
@dataclass
class SiteConfig:
    """Hold configuration data for a pluggable app site."""

    punctuation: str = "!"


@injectable()
@dataclass
class Greeter:
    """A simple greeter."""

    punctuation: str = get(SiteConfig, attr="punctuation")
    greeting: str = "Hello"

    def greet(self) -> str:
        """Provide a greeting."""
        return f"{self.greeting}{self.punctuation}"


def main() -> str:
    """Render a template to a string."""
    registry = Registry()
    registry.scan()
    # Later
    greeter = registry.get(Greeter)
    return greeter.greet()
