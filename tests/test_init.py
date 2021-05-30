"""Test suite for the hopscotch package."""
from hopscotch import hello


def test_hello() -> None:
    """Simple echo."""
    assert "World" == hello()
