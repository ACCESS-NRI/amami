# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0
import importlib.metadata
import importlib.util
import sys

# Lazy imports function
def lazy_import(name):
    """Function to implement lazy imports and speed up code in some cases"""
    spec = importlib.util.find_spec(name)
    if spec:
        loader = importlib.util.LazyLoader(spec.loader)
        spec.loader = loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        loader.exec_module(module)
        return module
    raise ModuleNotFoundError(f"No module named '{name}'")

# Set version
try:
    __version__ = importlib.metadata.version(__name__)
except importlib.metadata.PackageNotFoundError:
    import warnings
    __version__ = ""
    warnings.warn("Unable to interrogate version string from installed distribution.")

_C_END = '\033[0m'
_C_CMD = '\033[1;38;2;10;150;200m'
_C_DESC = '\033[0;38;2;150;100;30m'

__doc__ = """
AMAMI (ACCESS Models Ancillary Manipulation Instruments) is a multi-tool package"""\
""" to facilitate the manipulation of input and output files associated with ACCESS"""\
""" models and some of their components. For more information about ACCESS models"""\
f""" and components, please refer to https://access-hive.org.au/models/.

List of supported commands:
----------------------------------------------------
| command | description                             |
----------------------------------------------------
| {_C_CMD}um2nc{_C_END}   | {_C_DESC}Convert UM fieldsfile to netCDF.{_C_END}        |
| {_C_CMD}modify{_C_END}  | {_C_DESC}Modify UM fieldsfile based on netCDF.{_C_END}   |
----------------------------------------------------
For more information about a specific command, please run `amami <command> -h`.
"""
