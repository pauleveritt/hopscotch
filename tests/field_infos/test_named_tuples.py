"""Test the field discovery functions for named tuples."""
import typing

from hopscotch.field_infos import (
    get_field_origin,
)
from hopscotch.fixtures.named_tuples import Greeter
from hopscotch.fixtures.named_tuples import Greeting


def test_get_field_origin_no_generic() -> None:
    """Find correct type with *no* generic involved."""
    th = typing.get_type_hints(Greeter, globalns=None, localns=None)
    param1_annotation = th["greeting"]
    result = get_field_origin(param1_annotation)
    assert Greeting is result
