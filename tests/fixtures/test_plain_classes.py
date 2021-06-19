"""Make sure the test/example/docs examples work."""
from hopscotch.fixtures.plain_classes import Greeter
from hopscotch.fixtures.plain_classes import GreeterService
from hopscotch.fixtures.plain_classes import Greeting
from hopscotch.fixtures.plain_classes import GreetingService


def test_plain_old_greeting() -> None:
    """Check the example ``plain_class.Greeting``."""
    result = Greeting()
    assert result.salutation == "Hello"


def test_plain_old_greeting_service() -> None:
    """Check the example ``plain_class.GreetingService``."""
    result = GreetingService()
    assert result.salutation == "Hello"


def test_plain_old_greeter() -> None:
    """Check the example ``plain_class.Greeter``."""
    greeting = Greeting()
    result = Greeter(greeting=greeting)
    assert result.greeting.salutation == "Hello"


def test_plain_old_greeter_service() -> None:
    """Check the example ``plain_class.GreeterService``."""
    greeting = GreetingService()
    result = GreeterService(greeting=greeting)
    assert result.greeting.salutation == "Hello"
