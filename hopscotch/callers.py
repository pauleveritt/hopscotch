"""Utility functions for scanning packages and modules."""

def caller_module(level: int = 2, sys_mod: ModuleType = sys) -> ModuleType:
    getframe = getattr(sys_mod, "_getframe")
    module_globals = getframe(level).f_globals
    module_name = module_globals.get("__name__") or "__main__"
    modules = getattr(sys_mod, "modules")
    module: ModuleType = modules[module_name]
    return module
