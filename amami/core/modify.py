#!/usr/bin/env python3

# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

"""
Created by Davide Marchegiani at ACCESS-NRI - davide.marchegiani@anu.edu.au

Modify UM fieldsfile data using netCDF data, or by applying a user-defined
function.
"""

import argparse
import re
from amami.stash_utils import Stash
from amami.netcdf_utils import read_netCDF
import amami.um_utils as umutils
from amami.loggers import LOGGER
from amami.misc_utils import get_abspath

# ===== TO TEST
args = argparse.Namespace(
    subcommand='modify',
    verbose=None,
    silent=None,
    debug=True,
    infile='/g/data/tm70/dm5220/ancil/dietmar/qrparm.orog.original',
    outfile=None,
    ncfile='/g/data/tm70/dm5220/ancil/dietmar/qrparm.orog.original_modified.nc',
    ufunc=None,
    variables=None,
    latitude_name=None,
    longitude_name=None,
    time_name=None,
    level_name=None,
    nanval=None
)
# ========
def check_option_formats(ufunc, variables) -> None:
    '''
    Check that the option arguments are in the right formats
    '''
    #ARGUMENTS
    # --ufunc
    if ufunc is not None:
        if not re.match(r"^\s*lambda\s+",ufunc):
            LOGGER.error(
                "Invalid user-defined function.\n"
                "The function must be defined as a Python lambda function."
            )
        try:
            eval(ufunc)
        except SyntaxError:
            LOGGER.error(
                "Invalid Python lambda function defined.\n"
            )
    # --variables/--var
    if variables is not None:
        variables = variables.split()
        for var in variables:
            if not re.match(r"^((m\d{2})?s\d{2}i\d{3})|(\d{1,5})$",var):
                LOGGER.error(
                    f"Invalid variable STASH code '{var}'.\n"
                    "STASH code needs to be either an integer between 0 and 54999, "
                    "or a string in the format '[m--]s--i---', with each '-' being "
                    "an integer between 0-9.\nThe part wrapped in squared brackets "
                    "('[]') is optional."
                )

def check_variables_consistency(variables_arg,nvar_um,nvar_nc) -> None:
    '''
    Check that the number of variables in the UM file and in the netCDF file
    are consistent.
    '''
    if variables_arg is not None:
        nvar = len(variables_arg.split())
        if nvar > nvar_um:
            LOGGER.error(
                f"The number of selected variables ({nvar}) is "
                f"greater than the number of variables in the UM file ({nvar_um})."
            )
        sel = ' selected'
    else:
        nvar = nvar_um
        sel=''
    if nvar_nc != nvar:
        LOGGER.error(
            f"Number of{sel} variables in UM fieldsfile ({nvar}) "
            f"and netCDF file ({nvar_nc}) do not match.\nTo select "
            "a subset of variables to modify in the UM fieldsfile, "
            "use the '--var/--variables' option."
        )

def main(args: argparse.Namespace):
    """
    Main function for `modify` subcommand
    """
    LOGGER.debug(f"{args=}")
    # Get input path
    infile = get_abspath(args.infile)
    LOGGER.debug(f"{infile=}")
    # Get output path
    outfile = get_abspath(args.outfile, checkdir=True)
    LOGGER.debug(f"{outfile=}")
    # Check that options have the right formats
    check_option_formats(args.ufunc, args.variables)
    # Use mule to read the UM file
    LOGGER.info(f"Reading UM file {infile}")
    ff = umutils.read_fieldsfile(infile)
    if args.ncfile is not None:
        # Read netCDF file
        ncfile = get_abspath(args.ncfile)
        LOGGER.debug(f"{ncfile=}")
        LOGGER.info(f"Reading netCDF file {ncfile}")
        nc = read_netCDF(ncfile)
        # Check that the number of variables is consistent
        check_variables_consistency(
            args.variables,
            len(ff.fields),
            len(nc.data_vars),
        )
        
    else:
        # Use user-defined function
        pass
    LOGGER.info("Done!")
