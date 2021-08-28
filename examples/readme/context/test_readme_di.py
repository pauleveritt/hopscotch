"""Test the example."""


def test_readme_context() -> None:
    """We got a different greeter based on context."""
    from . import greeter1, greeter2

    assert greeter1.greeting == "Hello!"
    assert greeter2.greeting == "Bonjour!"
