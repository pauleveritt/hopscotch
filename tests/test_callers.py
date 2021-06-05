"""Test suite for caller utility functions."""
from hopscotch.callers import caller_module, caller_package
from .fixtures.init_caller_package import main as caller_init


def test_caller_module() -> None:
    """ Ensure the utility function returns the calling module """
    result = caller_module()
    assert "_pytest.python" == result.__name__


def test_caller_package() -> None:
    """ Ensure the utility function returns the calling package """
    result = caller_package()
    assert "_pytest" == result.__name__


def test_caller_package_init() -> None:
    """ Ensure the utility function returns the calling package init """
    result = caller_init()
    assert result.__name__ == 'tests.fixtures.init_caller_package'
