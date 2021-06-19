"""Make sure the test/example/docs examples work."""
from hopscotch.fixtures.dataklasses import Greeter
from hopscotch.fixtures.dataklasses import GreeterService
from hopscotch.fixtures.dataklasses import Greeting
from hopscotch.fixtures.dataklasses import GreetingService


def test_dataclass_greeting() -> None:
    """Check the example ``dataklass.Greeting``."""
    result = Greeting()
    assert result.salutation == "Hello"


def test_dataclass_greeting_service() -> None:
    """Check the example ``dataklass.GreetingService``."""
    result = GreetingService()
    assert result.salutation == "Hello"


def test_dataclass_greeter() -> None:
    """Check the example ``dataklass.Greeter``."""
    greeting = Greeting()
    result = Greeter(greeting=greeting)
    assert result.greeting.salutation == "Hello"


def test_dataclass_greeter_service() -> None:
    """Check the example ``dataklass.GreeterService``."""
    greeting = GreetingService()
    result = GreeterService(greeting=greeting)
    assert result.greeting.salutation == "Hello"
