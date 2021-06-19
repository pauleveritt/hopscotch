"""Test suite for caller utility functions."""
from hopscotch.callers import caller_module
from hopscotch.callers import caller_package
from hopscotch.fixtures.init_caller_package import main_package


def test_caller_module() -> None:
    """Ensure the utility function returns the calling module."""
    result = caller_module()
    assert "_pytest.python" == result.__name__


def test_caller_package() -> None:
    """Ensure the utility function returns the calling package."""
    result = caller_package()
    assert "_pytest" == result.__name__


def test_caller_package_init() -> None:
    """Ensure the utility function returns the calling package init."""
    result = main_package()
    assert result.__name__ == "tests.fixtures.init_caller_package"
