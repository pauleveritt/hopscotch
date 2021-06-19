"""Test the field discovery functions for plain classes."""
import typing
from dataclasses import dataclass

from hopscotch.field_infos import get_field_origin
from hopscotch.field_infos import get_operator
from hopscotch.fixtures.plain_classes import Greeter
from hopscotch.fixtures.plain_classes import GreeterAnnotated
from hopscotch.fixtures.plain_classes import GreeterOptional
from hopscotch.fixtures.plain_classes import GreeterService
from hopscotch.fixtures.plain_classes import Greeting
from hopscotch.fixtures.plain_classes import GreetingService


@dataclass()
class DummyGet:
    """Simulate an operator that looks something up."""

    arg: str

    def __call__(self) -> str:
        """Return the stored argument."""
        return self.arg


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


def test_get_operator() -> None:
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


# def test_dataclass_field_info_str() -> None:
#     @dataclass
#     class Foo:
#         customer_name: str
#
#     # Ensure this callable does not yet have the "cached" field info
#     assert not hasattr(Foo, "__hopscotch_predicates__")
#
#     field_infos = get_dataclass_field_infos(Foo)
#     assert field_infos[0].field_name == "customer_name"
#     assert field_infos[0].field_type == str
#     assert field_infos[0].default_value is None
#     assert field_infos[0].init is True
#
#     # Ensure the field info is stored on the callable, then
#     # try to get again.
#     assert hasattr(Foo, "__hopscotch_predicates__")
#     field_infos2 = get_dataclass_field_infos(Foo)
#     assert field_infos2 == field_infos
#
#
# def test_namedtuple_field_info_str() -> None:
#     class Foo(NamedTuple):
#         customer_name: str
#
#     # Ensure this callable does not yet have the "cached" field info
#     assert not hasattr(Foo, "__hopscotch_predicates__")
#
#     field_infos = get_non_dataclass_field_infos(Foo)
#     assert field_infos[0].field_name == "customer_name"
#     assert field_infos[0].field_type == str
#     assert field_infos[0].default_value is None
#     assert field_infos[0].init is True
#
#     # Ensure the field info is stored on the callable, then
#     # try to get again.
#     assert hasattr(Foo, "__hopscotch_predicates__")
#     field_infos2 = get_dataclass_field_infos(Foo)
#     assert field_infos2 == field_infos
#
#
# def test_poc_field_info_str() -> None:
#     class Foo:
#         customer_name: str
#
#         def __init__(self, customer_name: str):
#             self.customer_name = customer_name
#
#     field_infos = get_non_dataclass_field_infos(Foo)
#     assert field_infos[0].field_name == "customer_name"
#     assert field_infos[0].field_type == str
#     assert field_infos[0].default_value is None
#     assert field_infos[0].init is True
#
#
# def test_function_field_info_str() -> None:
#     def Foo(customer_name: str):
#         return customer_name
#
#     # Ensure this callable does not yet have the "cached" field info
#     assert not hasattr(Foo, "__hopscotch_predicates__")
#
#     field_infos = get_non_dataclass_field_infos(Foo)
#     assert field_infos[0].field_name == "customer_name"
#     assert field_infos[0].field_type == str
#     assert field_infos[0].default_value is None
#     assert field_infos[0].init is True
#
#     # Ensure the field info is stored on the callable, then
#     # try to get again.
#     assert hasattr(Foo, "__hopscotch_predicates__")
#     field_infos2 = get_dataclass_field_infos(Foo)
#     assert field_infos2 == field_infos
#
#
# def test_function_field_info_children() -> None:
#     def Foo(children):
#         return children
#
#     # Ensure this callable does not yet have the "cached" field info
#     assert not hasattr(Foo, "__hopscotch_predicates__")
#
#     field_infos = get_non_dataclass_field_infos(Foo)
#     assert field_infos[0].field_name == "children"
#     assert field_infos[0].field_type == tuple[VDOMNode]
#     assert field_infos[0].default_value is None
#     assert field_infos[0].init is True
#
#     # Ensure the field info is stored on the callable, then
#     # try to get again.
#     assert hasattr(Foo, "__hopscotch_predicates__")
#     field_infos2 = get_dataclass_field_infos(Foo)
#     assert field_infos2 == field_infos
#
#
# def test_dataclass_field_info_children() -> None:
#     @dataclass
#     class View:
#         children: tuple[VDOMNode]
#
#     field_infos = get_dataclass_field_infos(View)
#     assert field_infos[0].field_name == "children"
#     assert field_infos[0].field_type == tuple[VDOMNode]
#     assert field_infos[0].default_value is None
#     assert field_infos[0].init is True
#
#
# def test_dataclass_field_info_generic() -> None:
#     @dataclass
#     class View:
#         customer_name: Optional[str]
#
#     field_infos = get_dataclass_field_infos(View)
#     assert field_infos[0].field_name == "customer_name"
#     assert field_infos[0].field_type == str
#     assert field_infos[0].default_value is None
#     assert field_infos[0].init is True
#
#
# def test_namedtuple_dataclass_field_info_generic() -> None:
#     class View(NamedTuple):
#         customer_name: Optional[str]
#
#     field_infos = get_non_dataclass_field_infos(View)
#     assert field_infos[0].field_name == "customer_name"
#     assert field_infos[0].field_type == str
#     assert field_infos[0].default_value is None
#     assert field_infos[0].init is True
#
#
# def test_dataclass_field_info_more_generic() -> None:
#     @dataclass
#     class View:
#         customer_name: Tuple[str, ...]
#
#     field_infos = get_dataclass_field_infos(View)
#     assert field_infos[0].field_name == "customer_name"
#     ga = getattr(typing, "_GenericAlias")
#     assert isinstance(field_infos[0].field_type, ga)
#     assert field_infos[0].default_value is None
#     assert field_infos[0].init is True
#
#
# def test_dataclass_field_info_init_false() -> None:
#     @dataclass
#     class View:
#         customer_name: str = field(init=False)
#
#     field_infos = get_dataclass_field_infos(View)
#     assert field_infos[0].field_name == "customer_name"
#     assert field_infos[0].field_type == str
#     assert field_infos[0].default_value is None
#     assert field_infos[0].init is False
#     assert field_infos[0].has_annotated is False
#
#
# def test_dataclass_field_info_annotation() -> None:
#     @dataclass
#     class Get:
#         """ Simulate an operator that looks something up """
#
#         arg: str
#
#         def __call__(self):
#             return self.arg
#
#     @dataclass
#     class Bar:
#         foo: Annotated[
#             str,
#             DummyGet("some_arg"),  # noqa: F821
#         ]
#
#     field_infos = get_dataclass_field_infos(Bar)
#     assert field_infos[0].field_name == "foo"
#     assert field_infos[0].field_type is str
#     assert field_infos[0].default_value is None
#     assert isinstance(field_infos[0].operator, DummyGet)
#     assert field_infos[0].has_annotated is True
