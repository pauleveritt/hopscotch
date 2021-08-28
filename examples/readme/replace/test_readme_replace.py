"""Test the example."""


def test_readme_replace() -> None:
    """We got a different greeter."""
    from . import greeter

    assert greeter.greeting == "Howdy!"
