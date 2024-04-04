# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

# pylint: disable = missing-module-docstring
import importlib.metadata

# Set version
try:
    __version__ = importlib.metadata.version(__name__)
except importlib.metadata.PackageNotFoundError:
    import warnings
    __version__ = ""
    warnings.warn("Unable to interrogate version string from installed distribution.")

__author__ = "Davide Marchegiani (davide.marchegiani@anu.edu.au)"

_C_END = '\033[0m'
_C_CMD = '\033[1;38;2;10;150;200m'
_C_DESC = '\033[0;38;2;150;100;30m'

__doc__ = """
AMAMI (ACCESS Models Ancillary Manipulation Instruments) is a multi-tool package """\
"""to facilitate the manipulation of input and output files associated with ACCESS """\
"""models and some of their components. For more information about ACCESS models """\
f"""and components, please refer to https://access-hive.org.au/models/.

Created by {__author__} at ACCESS-NRI.
If you want to report any bugs, issues, or would like to request any functionality to be """\
"""added to the AMAMI package, please refer to the issue page of the GitHub repository: """\
f"""https://github.com/ACCESS-NRI/amami/issues.


List of supported commands:
-----------------------------------------------------------------------------
| command | description                                                      |
-----------------------------------------------------------------------------
| {_C_CMD}um2nc{_C_END}   | {_C_DESC}Convert UM fieldsfile to netCDF.{_C_END}                                 |
| {_C_CMD}modify{_C_END}  | {_C_DESC}Modify UM fieldsfile based on netCDF or user-defined function.{_C_END}   |
-----------------------------------------------------------------------------
For more information about a specific command, please run `amami <command> -h`.
"""
