"""Test the field discovery functions for named tuples."""
import typing

from hopscotch.field_infos import (
    get_field_origin, get_non_dataclass_field_infos,
)
from hopscotch.fixtures.named_tuples import Greeter, GreetingNoDefault
from hopscotch.fixtures.named_tuples import Greeting


def test_get_field_origin_no_generic() -> None:
    """Find correct type with *no* generic involved."""
    th = typing.get_type_hints(Greeter, globalns=None, localns=None)
    param1_annotation = th["greeting"]
    result = get_field_origin(param1_annotation)
    assert Greeting is result


def test_namedtuple_field_info_str():
    """Extract field info from a full target and check caching."""
    # Ensure this callable does not yet have the "cached" field info
    assert not hasattr(GreetingNoDefault, "__hopscotch_predicates__")

    field_infos = get_non_dataclass_field_infos(GreetingNoDefault)
    assert field_infos[0].field_name == "salutation"
    assert field_infos[0].field_type == str
    assert field_infos[0].default_value is None
    assert field_infos[0].init is True

    # Ensure the field info is stored on the callable, then
    # try to get again.
    assert hasattr(GreetingNoDefault, "__hopscotch_predicates__")
    field_infos2 = get_non_dataclass_field_infos(GreetingNoDefault)
    assert field_infos2 == field_infos
