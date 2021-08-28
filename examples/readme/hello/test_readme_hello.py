"""Test the example."""
from . import greeter


def test_readme_hello() -> None:
    """Make sure the greeter is retrieved from registry."""
    assert greeter.greeting == "Hello!"
