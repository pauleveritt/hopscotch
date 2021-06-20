"""Hopscotch."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping
from typing import Union

__all__ = [
    "VDOMNode",
]


@dataclass(frozen=True)
class VDOMNode:
    """Data for a container or item node in the VDOM tree."""

    __slots__ = ["tag", "props", "children"]
    tag: str
    props: Mapping[object, object]
    children: list[Union[str, VDOMNode]]
