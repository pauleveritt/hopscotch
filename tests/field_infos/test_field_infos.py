"""Test the field discovery functions for various targets."""
import typing

import pytest

from hopscotch.field_infos import get_field_origin
from hopscotch.fixtures import (
    dataklasses,
    functions,
    named_tuples,
    plain_classes,
)


@pytest.mark.parametrize(
    'target, expected',
    [
        (dataklasses.Greeter, dataklasses.Greeting),
        (functions.Greeter, functions.Greeting),
        (named_tuples.Greeter, named_tuples.Greeting),
        (plain_classes.Greeter, plain_classes.Greeting),
    ]
)
def test_get_field_origin_no_generic(target, expected) -> None:
    """Find correct type with *no* generic involved."""
    th = typing.get_type_hints(target, globalns=None, localns=None)
    param1_annotation = th["greeting"]
    actual = get_field_origin(param1_annotation)
    assert expected is actual
