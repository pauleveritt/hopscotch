"""Simple dependency injection."""
from dataclasses import dataclass
from hopscotch import injectable
from hopscotch import Registry


@injectable()
@dataclass
class SiteConfig:
    """Hold configuration data for a pluggable app site."""

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
