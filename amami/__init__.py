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
AMAMI (ACCESS Models Ancillary Manipulation Instruments)
"""