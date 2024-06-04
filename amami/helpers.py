# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

"""
Script created by Davide Marchegiani (davide.marchegiani@anu.edu.au) at ACCESS-NRI.

Miscellaneous module for different utility functions.
"""

import os


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


def create_unexistent_file(path):
    """
    Create a new file.
    """
    n=1
    newpath = path
    while os.path.exists(newpath):
        n+=1
        newpath = f"{path}_{n}"
    return newpath
