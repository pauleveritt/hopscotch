"""Test suite for caller utility functions."""
from hopscotch.callers import caller_module


def test_caller_module() -> None:
    result = caller_module()
    assert "_pytest.python" == result.__name__
