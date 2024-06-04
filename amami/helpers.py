# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

"""
Script created by Davide Marchegiani (davide.marchegiani@anu.edu.au) at ACCESS-NRI.

Miscellaneous module for different utility functions.
"""

import os
import itertools


# TODO: refactor/delete, let I/O ops raise IOErrors on missing files
def get_abspath(fpath: str, check: bool = True, checkdir: bool = False) -> str:
    """
    Return absolute path from given path.

    :param fpath:
    :param check:
    :param checkdir: True to check if base directory exists.
    """
    if checkdir:
        check = False
    abspath = os.path.abspath(fpath)

    if check and not os.path.exists(abspath):
        raise IOError(f"File '{abspath}' does not exist.")
    elif checkdir:
        absdir = os.path.dirname(abspath)

        if not os.path.exists(absdir):
            raise IOError(f"Directory '{absdir}' does not exist.")
    return abspath


# TODO: rename file --> path as func does not create the file
def create_unexistent_file(path):
    """
    Return unique file path by adding a numeric suffix.
    """
    for n in itertools.count(1):
        if not os.path.exists(new_path := f"{path}_{n}"):
            return new_path
