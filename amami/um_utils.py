# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

"""
Script created by Davide Marchegiani (davide.marchegiani@anu.edu.au) at ACCESS-NRI.

Utility module for UM fieldsfiles
"""

from typing import List
import mule
from amami.loggers import LOGGER

IMDI=-32768 #(-2.0**15)
RMDI=-1073741824.0 #(-2.0**30)

def read_fieldsfile(
    um_filename: str,
    check_ancil:bool=False
    ) -> type[mule.UMFile]:
    """Read UM fieldsfile with mule, and optionally check if type is AncilFile"""

    try:
        file = mule.load_umfile(um_filename)
        file.remove_empty_lookups()
    except ValueError:
        LOGGER.error(f"'{um_filename.resolve()}' does not appear to be a UM file.")
    if check_ancil and (not isinstance(file, mule.ancil.AncilFile)):
        LOGGER.error(f"'{um_filename}' does not appear to be a UM ancillary file.")
    return file

def get_grid_type(um_file:type[mule.UMFile]) -> str:
    """Get UM grid type from mule UMFile"""
    gs = um_file.fixed_length_header.grid_staggering
    if gs == 6:
        return 'EG' # End Game
    elif gs == 3:
        return 'ND' # New Dynamics
    else:
        LOGGER.error(
            "Unable to determine grid staggering from UM Fielsfile header. "\
            f"Grid staggering '{gs}' not supported."
        )

def get_sealevel_rho(um_file:type[mule.UMFile]) -> float:
    """Get UM sea level on rho levels from mule UMFile"""
    try:
        return um_file.level_dependent_constants.zsea_at_rho
    except AttributeError:
        return 0.

def get_sealevel_theta(um_file:type[mule.UMFile]) -> float:
    """Get UM sea level on thetha levels from mule UMFile"""
    try:
        return um_file.level_dependent_constants.zsea_at_theta
    except AttributeError:
        return 0.
    
def get_stash(
    um_file:type[mule.UMFile],
    repeat:bool=True,
) -> List:
    """
    Get ordered list of stash codes in mule UMFile
    with (repeat = True) or without (repeat = False) repetitions.
    """
    stash_codes = [f.lbuser4 for f in um_file.fields]
    if not repeat:
        return list(dict.fromkeys(stash_codes))
    return stash_codes