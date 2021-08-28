"""Simple dependency injection."""
from dataclasses import dataclass

from hopscotch import Registry, injectable
from hopscotch.operators import get


@injectable()
@dataclass
class SiteConfig:
    punctuation: str = "!"


@injectable()
@dataclass
class Greeter:
    """A simple greeter."""

    config: SiteConfig
    greeting: str = "Hello"

    def greet(self) -> str:
        """Provide a greeting."""
        return f"{self.greeting}{self.config.punctuation}"


registry = Registry()
registry.scan()
# Later
greeter = registry.get(Greeter)
greeting = greeter.greet()
# greeting == "Hello!"
