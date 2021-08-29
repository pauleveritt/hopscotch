"""Default operators for fields.

Operators allow a field to ask for some work to be done during injection.
"""
from __future__ import annotations

from dataclasses import dataclass
from dataclasses import Field
from dataclasses import field
from typing import Any
from typing import Optional
from typing import Protocol
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .registry import Registry


class Operator(Protocol):
    """Specify the structure of operator implementations."""

    def __call__(self, registry: Registry) -> str:
        """Operators are callables."""
        ...


def make_field_operator(operator_class: Any) -> Any:
    """Helper to convert an Operator into a dataclass field."""

    def _inner(*args, **kwargs) -> Field:  # type: ignore
        # Some of the kwargs are for generic field keyword
        # arguments, such as ``init=False``. But some should be
        # sent to the operator. Put them in two piles.
        operator_kwargs = {}
        for kwarg_key, kwarg_value in list(kwargs.items()):
            if kwarg_key not in Field.__slots__:
                operator_kwargs[kwarg_key] = kwarg_value
                del kwargs[kwarg_key]

        # We can now construct the operator
        operator = operator_class(*args, **operator_kwargs)
        if "metadata" not in kwargs:
            kwargs["metadata"] = {}

        # Use dataclass field metadata support to smuggle our injector
        # information through to the other side.
        kwargs["metadata"]["injected"] = dict(operator=operator)
        return field(**kwargs)  # type: ignore

    return _inner


# Start Get
@dataclass(frozen=True)
class Get:
    """Lookup a kind and optionally pluck an attr."""

    lookup_key: Any
    attr: Optional[str] = None

    def __call__(
        self,
        registry: Registry,
    ) -> object:
        """Use registry to find lookup key and optionally pluck attr."""
        # Can't lookup a string, ever, so bail on this with an error.
        if isinstance(self.lookup_key, str):
            lk = self.lookup_key
            msg = f"Cannot use a string '{lk}' as container lookup value"
            raise ValueError(msg)

        result_value = registry.get(self.lookup_key)

        # Are we plucking an attr?
        if self.attr is not None:
            result_value = getattr(result_value, self.attr)

        return result_value


get = make_field_operator(Get)


@dataclass(frozen=True)
class Context:
    """Grab the current container context and optionally pluck an attr."""

    attr: Optional[str] = None

    def __call__(
        self,
        registry: Registry,
    ) -> object:
        """Use registry to grab the context and optionally pluck an attr."""
        value = registry.context
        if value is None:
            raise ValueError("No context on registry")

        # Are we plucking an attr?
        if self.attr is not None:
            value = getattr(value, self.attr)

        return value


context = make_field_operator(Context)
