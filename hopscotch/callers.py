"""Utility functions for scanning packages and modules."""
import sys
from types import ModuleType
from typing import Callable


def caller_module(level: int = 2, sys_mod: ModuleType = sys) -> ModuleType:
    getframe = getattr(sys_mod, "_getframe")
    module_globals = getframe(level).f_globals
    module_name = module_globals.get("__name__") or "__main__"
    modules = getattr(sys_mod, "modules")
    module: ModuleType = modules[module_name]
    return module


def caller_package(
        level: int = 2,
        cm: Callable[
            [
                int,
            ],
            ModuleType,
        ] = caller_module,
) -> ModuleType:
    # cm caller_module in arg list for tests
    module = cm(level + 1)
    f = getattr(module, "__file__", "")
    if ("__init__.py" in f) or ("__init__$py" in f):  # empty at >>>
        # Module is a package
        return module
    # Go up one level to get package
    package_name = module.__name__.rsplit(".", 1)[0]
    return sys.modules[package_name]
