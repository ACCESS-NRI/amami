# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0
"""
Main amami module that sets docs, version, authors, command, and the consoles for output logging.
"""

import importlib.metadata

# Set version
try:
    __version__ = importlib.metadata.version(__name__)
except importlib.metadata.PackageNotFoundError:
    __version__ = ""
    # TODO: Add warning but change logic because this causes a circular import
    # from amami.loggers import LOGGER
    # LOGGER.warning(
    #     "Unable to interrogate version string from installed %s distribution.",
    #     __name__,
    # )

# Description of the package styled using rich markup
__doc__ = """
AMAMI (ACCESS Models Ancessory Manipulation Interface) is a multi-tool package to facilitate the \
manipulation of input and output files associated with ACCESS models and their components.
For more information about ACCESS models and components, please refer to https://access-hive.org.au/models/.

Created at ACCESS-NRI.
If you want to report any bugs, issues, or would like to request any functionality to be added to the \
AMAMI package, please refer to the issue page of the GitHub repository: https://github.com/ACCESS-NRI/amami/issues.

[argparse.groups]List of commands:[/]

 [bold]Command[/]   [bold]Description[/]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 [rgb(10,150,200)]um2nc[/]     [rgb(215,175,30)]Convert a UM fieldsfile to netCDF.[/]

For more information about a specific command, run `amami <command> -h`.
"""

# Store the command that gets called so that it can be accessed by any module
__command__ = None
