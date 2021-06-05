"""Sample package with a __init__.py

Used for testing caller_package and the branching that looks
if the package has a __init__.py in it.
"""
from hopscotch.callers import caller_package


def make_call():
    return caller_package()


def main():
    return make_call()
