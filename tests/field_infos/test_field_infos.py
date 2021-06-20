"""Test the field discovery functions for various targets."""
import typing

import pytest

from hopscotch import VDOMNode
from hopscotch.field_infos import (
    get_field_origin,
    get_operator,
    get_non_dataclass_field_infos,
    get_dataclass_field_infos,
)
from hopscotch.fixtures import (
    dataklasses,
    functions,
    named_tuples,
    plain_classes,
    DummyGet,
)
from hopscotch.fixtures.dataklasses import GreetingOperator, GreetingTuple


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


@pytest.mark.parametrize(
    'target, expected',
    [
        (dataklasses.GreeterOptional, dataklasses.Greeting),
        (functions.GreeterOptional, functions.Greeting),
        (named_tuples.GreeterOptional, named_tuples.Greeting),
        (plain_classes.GreeterOptional, plain_classes.Greeting),
    ]
)
def test_get_field_origin_generic(target, expected) -> None:
    """Find correct type with a generic involved."""
    th = typing.get_type_hints(target, globalns=None, localns=None)
    param1_annotation = th["greeting"]
    result = get_field_origin(param1_annotation)
    assert expected is result


@pytest.mark.parametrize(
    'target, expected',
    [
        (dataklasses.GreeterAnnotated, dataklasses.Greeting),
        (functions.GreeterAnnotated, functions.Greeting),
        (named_tuples.GreeterAnnotated, named_tuples.Greeting),
        (plain_classes.GreeterAnnotated, plain_classes.Greeting),
    ]
)
def test_get_field_origin_annotated(target, expected) -> None:
    """Find correct type with an ``Annotated`` involved."""
    th = typing.get_type_hints(target, globalns=None, localns=None)
    param1_annotation = th["greeting"]
    result = get_field_origin(param1_annotation)
    assert expected is result


@pytest.mark.parametrize(
    'target',
    [
        dataklasses.Greeting,
        functions.Greeting,
        named_tuples.Greeting,
        plain_classes.Greeting,
    ]
)
def test_get_field_origin_primitive_type(target) -> None:
    """Find correct type with a primitive type like ``str``."""
    th = typing.get_type_hints(target, globalns=None, localns=None)
    param1_annotation = th["salutation"]
    result = get_field_origin(param1_annotation)
    assert str is result


def test_dummy_get_operator() -> None:
    """See if we can get the annotation to get the operator."""
    field_type = typing._AnnotatedAlias(str, (DummyGet("some_arg"),))
    field_type, operator = get_operator(field_type)
    assert str is field_type
    assert "some_arg" == operator()


def test_get_operator_no_annotated() -> None:
    """A field with no ``Annotated`` shouldn't fail on get_operator.

    This simulates a field like ``title: str`` with no ``Annotated`` nor
    operator.
    """
    field_type = str
    field_type, operator = get_operator(field_type)
    assert str is field_type
    assert None is operator


@pytest.mark.parametrize(
    'target, extractor',
    [
        (dataklasses.GreetingNoDefault, get_dataclass_field_infos),
        (functions.GreetingNoDefault, get_non_dataclass_field_infos),
        (named_tuples.GreetingNoDefault, get_non_dataclass_field_infos),
        (plain_classes.GreetingNoDefault, get_non_dataclass_field_infos),
    ]
)
def test_target_field_info_str(target, extractor):
    """Extract field info from a full target and check caching."""
    # Ensure this callable does not yet have the "cached" field info
    assert not hasattr(target, "__hopscotch_predicates__")

    field_infos = extractor(target)
    assert field_infos[0].field_name == "salutation"
    assert field_infos[0].field_type == str
    assert field_infos[0].default_value is None
    assert field_infos[0].init is True

    # Ensure the field info is stored on the callable, then
    # try to get again.
    assert hasattr(target, "__hopscotch_predicates__")
    field_infos2 = get_non_dataclass_field_infos(target)
    assert field_infos2 == field_infos


@pytest.mark.parametrize(
    'target, extractor',
    [
        (dataklasses.GreeterChildren, get_dataclass_field_infos),
        (functions.GreeterChildren, get_non_dataclass_field_infos),
        (named_tuples.GreeterChildren, get_non_dataclass_field_infos),
        (plain_classes.GreeterChildren, get_non_dataclass_field_infos),
    ]
)
def test_field_info_children(target, extractor) -> None:
    """Look for the magic-named ``children`` argument."""
    field_infos = extractor(target)
    assert field_infos[0].field_name == "children"
    assert field_infos[0].field_type == tuple[VDOMNode]
    assert field_infos[0].default_value is None
    assert field_infos[0].init is True


def test_dataclass_field_info_init_false() -> None:
    """Look for the field constructor and init false."""
    field_infos = get_dataclass_field_infos(dataklasses.GreetingInitFalse)
    assert field_infos[0].field_name == "salutation"
    assert field_infos[0].field_type == str
    assert field_infos[0].default_value is None
    assert field_infos[0].init is False
    assert field_infos[0].has_annotated is False


def test_field_info_more_generic() -> None:
    """Look up a field that is a generic using ``tuple``."""
    field_infos = get_dataclass_field_infos(GreetingTuple)
    assert field_infos[0].field_name == "salutation"
    assert "GenericAlias" in str(type(field_infos[0].field_type))
    assert field_infos[0].default_value is None
    assert field_infos[0].init is True


def test_dataclass_field_info_annotation() -> None:
    """Resolve an ``Annotated`` that uses an operator."""
    field_infos = get_dataclass_field_infos(GreetingOperator)
    assert field_infos[0].field_name == "salutation"
    assert field_infos[0].field_type is str
    assert field_infos[0].default_value is None
    assert isinstance(field_infos[0].operator, DummyGet)
    assert field_infos[0].has_annotated is True
