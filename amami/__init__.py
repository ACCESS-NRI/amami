# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

import importlib.metadata
from amami.loggers import LOGGER

# Set version
try:
    __version__ = importlib.metadata.version(__name__)
except importlib.metadata.PackageNotFoundError:
    __version__ = ""
    LOGGER.warning("Unable to interrogate version string from installed amami distribution.")

__authors__ = [
    "Davide Marchegiani <davide.marchegiani@anu.edu.au>",
    "Ben Davies <Ben.Davies@anu.edu.au>",
]
if len(__authors__) >1:
    AUTORS_STRING = ", ".join(__authors__[:-1])+f" and {__authors__[-1]}"
else:
    AUTORS_STRING = __authors__[0]

_C_END = '\033[0m'
_C_CMD = '\033[1;38;2;10;150;200m'
_C_DESC = '\033[0;38;2;150;100;30m'

__doc__ = """
AMAMI (ACCESS Models Ancillary Manipulation Instruments) is a multi-tool package """\
"""to facilitate the manipulation of input and output files associated with ACCESS """\
"""models and their components. For more information about ACCESS models """\
f"""and components, please refer to https://access-hive.org.au/models/.

Created by {AUTORS_STRING} at ACCESS-NRI.
If you want to report any bugs, issues, or would like to request any functionality to be """\
"""added to the AMAMI package, please refer to the issue page of the GitHub repository: """\
f"""https://github.com/ACCESS-NRI/amami/issues.


List of supported commands:
------------------------------------------------------------------------------------------------
| command | description                                                                        |
------------------------------------------------------------------------------------------------
| {_C_CMD}um2nc{_C_END}   | {_C_DESC}Convert a UM fieldsfile to netCDF.{_C_END}                                                 |
| {_C_CMD}modify{_C_END}  | {_C_DESC}Modify a UM fieldsfile using data from a netCDF file, or a user-defined function.{_C_END}  |
------------------------------------------------------------------------------------------------
For more information about a specific command, run `amami <command> -h`.
"""
