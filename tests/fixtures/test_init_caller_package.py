"""Test example at ``fixturs.init_caller_package``."""
from hopscotch.fixtures import init_caller_package


def test_init_caller_package() -> None:
    """Test the fixture at tests.fixtures.init_caller_package."""
    result = init_caller_package.main_package()
    assert init_caller_package == result
