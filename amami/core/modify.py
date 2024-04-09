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
import numpy as np
from mule import ArrayDataProvider
from amami.stash_utils import Stash
from amami.netcdf_utils import read_netCDF
from amami.um_utils import (
    read_fieldsfile, 
    get_stash, 
    UM_NANVAL,
)
from amami.loggers import LOGGER
from amami.misc_utils import get_abspath

def check_option_formats(
    ufunc_arg, 
    stash_codes_arg
) -> None:
    '''
    Check that the option arguments are in the right formats.
    '''
    #ARGUMENTS
    # --ufunc
    if ufunc_arg is not None:
        if not re.match(r"^\s*lambda\s+",ufunc_arg):
            LOGGER.error(
                "Invalid user-defined function.\n"
                "The function must be defined as a Python lambda function."
            )
        try:
            eval(ufunc_arg)
        except SyntaxError:
            LOGGER.error(
                "Invalid Python lambda function defined.\n"
            )
    # --stash
    if stash_codes_arg is not None:
        for var in stash_codes_arg.split():
            if not re.match(r"^((m\d{2})?s\d{2}i\d{3})|(\d{1,5})$",var):
                LOGGER.error(
                    "Invalid variable STASH code '%s'.\n"
                    "STASH code needs to be either an integer between 0 and 54999, "
                    "or a string in the format '[m--]s--i---', with each '-' being "
                    "an integer between 0-9.\nThe part wrapped in squared brackets "
                    "('[]') is optional.",
                    var
                )

def check_variables_consistency(
    stash_codes_arg,
    nvar_um,
    nvar_nc
) -> None:
    '''
    Check that the number of variables in the UM file and in the netCDF file
    are consistent.
    '''
    if stash_codes_arg is not None:
        num_stash_codes = len(stash_codes_arg.split())
        if num_stash_codes > nvar_um:
            LOGGER.error(
                "The number of specified STASH codes (%d) is "
                "greater than the number of variables in the UM file (%d).",
                num_stash_codes,
                nvar_um,
            )
        elif nvar_nc != num_stash_codes:
            LOGGER.error(
                "The number of specified STASH codes (%d) "
                "and the number of netCDF variables (%d) do not match.\n"
                "For more information about the --stash option, run `amami modify --help`.",
                num_stash_codes,
                nvar_um,
            )
    else:
        if nvar_nc != nvar_um:
            LOGGER.error(
                "The number of UM variables (%d) "
                "and the number of netCDF variables (%d) do not match.\n"
                "To select specific UM variables to modify, use the --stash option.\n"
                "For more information about the --stash option, run `amami modify --help`.",
                nvar_um,
                nvar_nc,
            )

def check_coordinates_consistency(
    args,
    nc,
) -> None:
    '''
    Check that the number of specified coordinate names and 
    number of netCDF variables are consistent.
    '''
    coords = [
        'latitude',
        'longitude',
        'time',
        'level',
    ]
    argument_names = [getattr(args,f'{c}_name').split() if getattr(args,f'{c}_name') is not None else None for c in coords]
    option_names = [
        '--lat/--latitude',
        '--lon/--longitude',
        '--t/--time',
        '--lev/--level',
    ]
    for coord,arg,opt in zip(coords,argument_names,option_names):
        if (
            (arg is not None) 
            and 
            (len(arg) > 1) 
            and 
            (len(arg) != len(nc.data_vars))
        ):
                LOGGER.error(
                    "The number of %s dimension names specified (%d) "
                    "is different from the number of variables in the netCDF file (%d).\n"
                    "For more information about the %s option, run `amami modify --help`.",
                    coord,
                    len(arg.split()),
                    len(nc.data_vars),
                    opt,
                )

def get_stash_index(
    fieldsfile_stash_codes,
    stash_code,
) -> int:
    try:
        return fieldsfile_stash_codes.index(Stash(stash_code).itemcode)
    except ValueError:
        LOGGER.error(
            "Provided STASH code '%s' not found in UM fieldsfile.",
            stash_code
        )

# ===== TO TEST
args = argparse.Namespace(
    subcommand='modify',
    verbose=None,
    silent=None,
    debug=True,
    infile='/g/data/tm70/dm5220/ancil/amami_test/test.ancil',
    outfile='/g/data/tm70/dm5220/ancil/amami_test/test.ancil_modified',
    ncfile='/g/data/tm70/dm5220/ancil/amami_test/test.nc',
    # ncfile=None,
    # ufunc="lambda x: x+1",
    ufunc=None,
    # stash_codes="33 m01s00i036",
    stash_codes=None,
    latitude_name=None,
    longitude_name=None,
    time_name=None,
    level_name=None,
    nanval=None
)
# ========
def main(args: argparse.Namespace):
    """
    Main function for `modify` subcommand
    """
    LOGGER.debug(
        "args = %s",
        args,
    )
    exit()
    # Get input path
    infile = get_abspath(args.infile)
    LOGGER.debug(
        "infile = %s",
        infile,
    )
    # Get output path
    outfile = get_abspath(args.outfile, checkdir=True)
    LOGGER.debug(
        "outfile = %s",
        outfile,
    )
    # Check that options have the right formats
    check_option_formats(args.ufunc, args.stash_codes)
    # Use mule to read the UM file
    LOGGER.info(
        "Reading UM file %s",
        infile,
    )
    ff = read_fieldsfile(infile)
    if args.ncfile is not None:
        # Read netCDF file
        ncfile = get_abspath(args.ncfile)
        LOGGER.debug(
            "ncfile = %s",
            ncfile,
        )
        LOGGER.info(
            "Reading netCDF file %s",
            ncfile,
        )
        nc = read_netCDF(ncfile)
        # Check that the number of variables is consistent
        check_variables_consistency(
            args.stash_codes,
            len(ff.fields),
            len(nc.data_vars),
        )
        # Check coordinates consistency
        check_coordinates_consistency(
            args,
            nc,
        )
        ncvars=iter(nc.data_vars.values())
    else:
        # Use user-defined function
        LOGGER.info(
            "Setting user-defined function to '%s'",
            args.ufunc,
        )
        ufunc = eval(args.ufunc)
    # Copy fieldsfile, to modify it
    ff_new = ff.copy(include_fields=True)
    # Get UM fieldsfile iterable
    ff_new_fields = iter(ff_new.fields)
    # Get list of stash codes of UM fieldsfile
    ff_stash_codes = get_stash(ff)
    if args.stash_codes is not None:
        # If --stash option is specified, get indices of um variables with the selected stash codes
        ff_stash_ind = [get_stash_index(ff_stash_codes,stash_code) for stash_code in args.stash_codes.split()]
    else:
        # otherwise get indices of all um variables
        ff_stash_ind = range(len(ff.fields))
    LOGGER.info(
        "The following UM variables will be modified:\n"
        "\n".join([Stash(ff.fields[ind].lbuser4).__repr__() for ind in ff_stash_ind])
    )
    # Modify fieldsfile
    for ind in ff_stash_ind:
        LOGGER.info(
            "Modifying %s",
            Stash(ff_new.fields[ind].lbuser4),
        )
        data = ff_new.fields[ind].get_data()
        if args.ncfile is not None:
            ncvar = next(ncvars)
            default_lat_names = ("latitude","lat")
            if args.latitude_name is not None:
                lat_names = iter(args.latitude_name.split())
            else:
                lat_names = (default_lat_names for _ in range(len(ff_stash_ind)))
            lat = next(lat_names)
            try:
                cind = min(np.where([coord in ncvar.coords for coord in lat])[0])
            except ValueError:
                LOGGER.error(
                    "Specified latitude dimension name '%s' not found in netCDF variable '%s'.",
                    lat,
                    ncvar.name,
                )
            

            
        else:
            data_new = ufunc(data)
        ff_new.fields[ind].set_data_provider(ArrayDataProvider(data_new))
    LOGGER.info(
        "Writing UM fieldsfile %s",
        outfile,
    )
    ff_new.to_file(outfile)
    LOGGER.info("Done!")
