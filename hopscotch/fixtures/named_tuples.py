"""Example objects and services implemented as ``NamedTuple``.

Note that, since ``typing.NamedTuple`` doesn't really do inheritance,
we can't implement a ``Service`` as a ``NamedTuple``.
"""
from typing import NamedTuple


class Greeting(NamedTuple):
    """A ``NamedTuple`` to give a greeting."""

    salutation: str = "Hello"


class Greeter(NamedTuple):
    """A ``NamedTuple`` to engage a customer."""

    greeting: Greeting
