"""Sample package with a __init__.py for discovery.

Used for testing caller_package and the branching that looks
if the package has a __init__.py in it.
"""
from hopscotch.callers import caller_package


def make_call():
    """Simulate something that is called and looks back for caller."""
    return caller_package()


def main_package():
    """Simulate something that does the calling."""
    return make_call()
