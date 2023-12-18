"""Utility functions for scanning packages and modules."""
import sys
from types import ModuleType
from typing import Callable


def caller_module(level: int = 2) -> ModuleType | None:
    """Return the module of the caller of the current scope."""
    getframe = getattr(sys, "_getframe")
    module_globals = getframe(level).f_globals
    module_name = module_globals.get("__name__") or "__main__"
    if module_name == "__test__":
        # We are running from a doctest via Sybil so
        # don't try to sniff around
        return None
    module: ModuleType = sys.modules[module_name]
    return module


def caller_package(
    level: int = 2,
    cm: Callable[
        [
            int,
        ],
        ModuleType,
    ] = caller_module,
) -> ModuleType | None:
    """Return the package for the caller of a certain scope."""
    module = cm(level + 1)
    if module is None:
        # We are in a doctest via Sybl
        return None
    f = getattr(module, "__file__", "")
    if ("__init__.py" in f) or ("__init__$py" in f):  # empty at >>>
        # Module is a package
        return module
    # Go up one level to get package
    package_name = module.__name__.rsplit(".", 1)[0]
    return sys.modules[package_name]
