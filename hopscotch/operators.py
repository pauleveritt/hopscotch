"""Default operators for fields.

Operators allow a field to ask for some work to be done during injection.
"""
from __future__ import annotations

from dataclasses import dataclass
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


@dataclass(frozen=True)
class Get:
    """Lookup a service and optionally pluck an attr."""

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

        result_value = registry.get_service(self.lookup_key)

        # Are we plucking an attr?
        if self.attr is not None:
            result_value = getattr(result_value, self.attr)

        return result_value


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
