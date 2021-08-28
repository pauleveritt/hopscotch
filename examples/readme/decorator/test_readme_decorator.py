"""Test the example."""


def test_readme_decorator() -> None:
    """Make sure the greeter is retrieved from registry."""
    from . import greeter
    assert greeter.greeting == "Hello!"
