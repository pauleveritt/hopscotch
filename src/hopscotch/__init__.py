"""Hopscotch."""
from __future__ import annotations

from hopscotch.registry import inject_callable
from hopscotch.registry import injectable
from hopscotch.registry import Registration
from hopscotch.registry import Registry

__all__ = [
    "Registry",
    "injectable",
    "inject_callable",
    "Registration",
]
