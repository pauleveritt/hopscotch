"""Introspect target types and normalize to standard field info."""
from __future__ import annotations

import inspect
import os
import sysconfig
from dataclasses import Field
from dataclasses import fields
from dataclasses import is_dataclass
from dataclasses import MISSING
from inspect import Parameter
from inspect import signature
from typing import Any
from typing import Callable
from typing import get_args
from typing import get_origin
from typing import get_type_hints
from typing import NamedTuple
from typing import Optional
from typing import Tuple
from typing import Type
from typing import TYPE_CHECKING
from typing import Union

if TYPE_CHECKING:
    from hopscotch.operators import Operator

EMPTY = getattr(inspect, "_empty")


# At startup, make a set containing all the builtin module names
def get_stdlib_module_names() -> set[str]:
    """Called at startup to get a list of builtin modules."""
    stdlib_dir = sysconfig.get_path(name="stdlib")
    stdlib_modules = {f.replace(".py", "") for f in os.listdir(stdlib_dir)}
    # Add builtin "module" for things like tuple.
    stdlib_modules.add("builtins")
    return stdlib_modules


STDLIB_MODULE_NAMES = get_stdlib_module_names()


class FieldInfo(NamedTuple):
    """Extract needed info from dataclass fields, functions, etc."""

    field_name: str
    field_type: Optional[type]
    default_value: Optional[object] = None
    default_factory: Optional[Callable[[], object]] = None
    operator: Optional[Operator] = None
    has_annotated: bool = False
    is_builtin: bool = False


FieldInfos = list[FieldInfo]


def get_field_origin(field_type: Type[Any]) -> Any:
    """Helper to extract generic origin e.g. Optional[Resource]."""
    origin = get_origin(field_type)
    args = get_args(field_type)
    if origin is Union and args[-1] is type(None):  # noqa: E721
        return args[0]
    else:
        return field_type


def get_operator(field_type: Type[Any]) -> Tuple[type, Optional[Operator]]:
    """If using Annotation, get the operator."""
    operator = None
    if hasattr(field_type, "__metadata__"):
        field_type, operator = get_args(field_type)

    return field_type, operator


def dataclass_field_info_factory(field_type: type, field: Field[Any]) -> FieldInfo:
    """Return field metadata for a dataclass."""
    if field.name == "children":
        # Special case: a parameter named 'children'
        field_type = None
    else:
        # Is this a generic, such as Optional[KindContainer]?
        field_type = get_field_origin(field_type)

    # Using Annotation[] ??
    has_annotated = hasattr(field_type, "__metadata__")
    if has_annotated:
        field_type, operator = get_operator(field_type)
    else:
        # Field operators stash their info in field.metadata
        if "injected" in field.metadata:
            injected = field.metadata["injected"]
            operator = injected["operator"]
        else:
            operator = None

    # Default values
    default_value = None if field.default is MISSING else field.default
    default_factory = (
        None if field.default_factory is MISSING else field.default_factory
    )

    is_builtin = field_type.__module__ in STDLIB_MODULE_NAMES if field_type else False

    return FieldInfo(
        field_name=field.name,
        field_type=field_type,
        default_value=default_value,
        default_factory=default_factory,
        operator=operator,
        has_annotated=has_annotated,
        is_builtin=is_builtin,
    )


def function_field_info_factory(field_type: type, parameter: Parameter) -> FieldInfo:
    """Extract field info from a plain function."""
    operator = None
    is_builtin = False
    has_annotated = False

    this_field_type: Optional[type]
    if parameter.name == "children":
        # Special case: a parameter named 'children'
        this_field_type = None
    elif field_type == EMPTY:
        # If no type hint was provided, ``inspect._empty`` will be assigned.
        # Change this to None.
        this_field_type = None
    else:
        # Is this a generic, such as Optional[KindContainer]?
        this_field_type = get_field_origin(field_type)

        # Using Annotation[] ??
        if this_field_type:
            has_annotated = hasattr(this_field_type, "__metadata__")
            this_field_type, operator = get_operator(this_field_type)
            is_builtin = this_field_type.__module__ in STDLIB_MODULE_NAMES

    # Default values
    if parameter.default == EMPTY:
        default_value = None
    else:
        default_value = parameter.default

    return FieldInfo(
        field_name=parameter.name,
        field_type=this_field_type,
        default_value=default_value,
        operator=operator,
        has_annotated=has_annotated,
        is_builtin=is_builtin,
    )


def get_dataclass_field_infos(target: Callable[..., Any]) -> list[FieldInfo]:
    """Entry point to all sniffing at dataclasses."""
    type_hints = get_type_hints(
        target, include_extras=True, globalns=None, localns=None
    )
    # noinspection PyDataclass
    fields_mapping = {f.name: f for f in fields(target)}
    field_infos = [
        dataclass_field_info_factory(
            type_hints[field_name],
            fields_mapping[field_name],
        )
        for field_name in type_hints
    ]

    return field_infos


def get_non_dataclass_field_infos(target: Callable[..., Any]) -> list[FieldInfo]:
    """Entry point to all sniffing at non-dataclasses."""
    type_hints = get_type_hints(
        target, include_extras=True, globalns=None, localns=None
    )
    sig = signature(target)
    parameters = sig.parameters.values()
    field_infos = [
        function_field_info_factory(
            type_hints.get(param.name, param.annotation),
            param,
        )
        for param in parameters
    ]

    return field_infos


def get_field_infos(target: Any) -> FieldInfos:
    """Return field info for all the fields on a target."""
    if is_dataclass(target):
        return get_dataclass_field_infos(target)
    else:
        return get_non_dataclass_field_infos(target)
