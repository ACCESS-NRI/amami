# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0
import importlib.metadata

try:
    __version__ = importlib.metadata.version(__name__)
except importlib.metadata.PackageNotFoundError:
    import warnings
    __version__ = ""
    warnings.warn("Unable to interrogate version string from installed distribution.")

__doc__ = """
AMAMI (ACCESS Models Ancillary Manipulation Instruments) is a multi-tool package"""\
""" to facilitate the manipulation of input and output files associated with ACCESS"""\
""" models and some of their components. For more information about ACCESS models"""\
""" and components, please refer to https://access-hive.org.au/models/.

List of supported commands:
- um2nc -> Convert UM fieldsfile to netCDF.

For more information about a specific command, please run `amami <command> -h`.
"""
