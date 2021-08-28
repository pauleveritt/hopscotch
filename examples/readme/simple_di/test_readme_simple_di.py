"""Test the example."""


def test_readme_operators() -> None:
    """Construct a greeting from config."""
    from . import greeting
    assert greeting == "Hello!"
