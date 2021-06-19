"""Test the field discovery functions for named tuples."""
import typing

from hopscotch.field_infos import (
    get_field_origin,
    get_dataclass_field_infos,
)
from hopscotch.fixtures.dataklasses import Greeter, GreetingNoDefault
from hopscotch.fixtures.dataklasses import GreeterAnnotated
from hopscotch.fixtures.dataklasses import GreeterOptional
from hopscotch.fixtures.dataklasses import GreeterService
from hopscotch.fixtures.dataklasses import Greeting
from hopscotch.fixtures.dataklasses import GreetingService


def test_get_field_origin_no_generic() -> None:
    """Find correct type with *no* generic involved."""
    th = typing.get_type_hints(Greeter, globalns=None, localns=None)
    param1_annotation = th["greeting"]
    result = get_field_origin(param1_annotation)
    assert Greeting is result


def test_get_field_origin_service_no_generic() -> None:
    """Find correct type on a ``Service`` with *no* generic involved."""
    th = typing.get_type_hints(GreeterService, globalns=None, localns=None)
    param1_annotation = th["greeting"]
    result = get_field_origin(param1_annotation)
    assert GreetingService is result


def test_get_field_origin_generic() -> None:
    """Find correct type with a generic involved."""
    th = typing.get_type_hints(GreeterOptional, globalns=None, localns=None)
    param1_annotation = th["greeting"]
    result = get_field_origin(param1_annotation)
    assert Greeting is result


def test_get_field_origin_annotated() -> None:
    """Find correct type with an ``Annotated`` involved."""
    th = typing.get_type_hints(GreeterAnnotated, globalns=None, localns=None)
    param1_annotation = th["greeting"]
    result = get_field_origin(param1_annotation)
    assert Greeting is result


def test_get_field_origin_primitive_type() -> None:
    """Find correct type with a primitive type like ``str``."""
    th = typing.get_type_hints(Greeting, globalns=None, localns=None)
    param1_annotation = th["salutation"]
    result = get_field_origin(param1_annotation)
    assert str is result


def test_dataclass_field_info_str():
    """Extract field info from a full target and check caching."""
    # Ensure this callable does not yet have the "cached" field info
    assert not hasattr(GreetingNoDefault, "__hopscotch_predicates__")

    field_infos = get_dataclass_field_infos(GreetingNoDefault)
    assert field_infos[0].field_name == "salutation"
    assert field_infos[0].field_type == str
    assert field_infos[0].default_value is None
    assert field_infos[0].init is True

    # Ensure the field info is stored on the callable, then
    # try to get again.
    assert hasattr(GreetingNoDefault, "__hopscotch_predicates__")
    field_infos2 = get_dataclass_field_infos(GreetingNoDefault)
    assert field_infos2 == field_infos
