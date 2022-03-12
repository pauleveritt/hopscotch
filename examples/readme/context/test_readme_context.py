"""Test an example."""
from . import main


def test_main() -> None:
    """Ensure the result matches what is expected."""
    assert main() == ("Hello!", "Bonjour!")
