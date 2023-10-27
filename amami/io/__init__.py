# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0
"""
Script created by Davide Marchegiani (davide.marchegiani@anu.edu.au) at ACCESS-NRI.

Utility module for input/output file checking
"""
# pylint: disable=no-member

import os
from amami.loggers import LOGGER

def get_abspath(
    fpath:str,
    check:bool=True
    ) -> str:
    """
    Return an absolute path from the provided path and optionally check if path exists.
    """
    abspath = os.path.abspath(fpath)
    if check and not os.path.exists(abspath):
        LOGGER.error(f"'{abspath}' does not exist.")
    return abspath
