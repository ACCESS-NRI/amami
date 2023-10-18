#!/usr/bin/env python3

import importlib.util
import sys
from types import ModuleType

def mem():
    from psutil import Process
    import os
    process = Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)
class LazyImport:
    def __init__(self):
        pass

    def __new__(
            cls,
            name: str,
    ) -> type(ModuleType):
        try:
            return sys.modules[name]
        except KeyError:
            spec = importlib.util.find_spec(name)
            if spec:
                loader = importlib.util.LazyLoader(spec.loader)
                spec.loader = loader
                module = importlib.util.module_from_spec(spec)
                sys.modules[name] = module
                loader.exec_module(module)
                return module
            else:
                raise ModuleNotFoundError(f"No module named '{name}'") from None
