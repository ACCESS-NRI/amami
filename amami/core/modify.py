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
from mule import ArrayDataProvider
from amami.stash_utils import Stash
from amami.netcdf_utils import read_netCDF
from amami.um_utils import read_fieldsfile, get_stash
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
                    f"Invalid variable STASH code '{var}'.\n"
                    "STASH code needs to be either an integer between 0 and 54999, "
                    "or a string in the format '[m--]s--i---', with each '-' being "
                    "an integer between 0-9.\nThe part wrapped in squared brackets "
                    "('[]') is optional."
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
                f"The number of specified STASH codes ({num_stash_codes}) is "
                f"greater than the number of variables in the UM file ({nvar_um})."
            )
        elif nvar_nc != num_stash_codes:
            LOGGER.error(
                f"The number of specified STASH codes ({num_stash_codes}) "
                f"and the number of netCDF variables ({nvar_nc}) do not match.\n"
                "For more information about the --stash option, run `amami modify --help`."
            )
    else:
        if nvar_nc != nvar_um:
            LOGGER.error(
                f"The number of UM variables ({nvar_um}) "
                f"and the number of netCDF variables ({nvar_nc}) do not match.\n"
                "To select specific UM variables to modify, use the --stash option.\n"
                "For more information about the --stash option, run `amami modify --help`."
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
        if arg is not None:
            if (len(arg) > 1) and (len(arg) != len(nc.data_vars)):
                LOGGER.error(
                    f"The number of {coord} dimension names specified ({len(arg.split())}) "
                    f"is different from the number of variables in the netCDF file ({len(nc.data_vars)}).\n"
                    f"For more information about the {opt} option, run `amami modify --help`."
                )

def get_stash_index(
    fieldsfile_stash_codes,
    stash_code,
) -> int:
    try:
        return fieldsfile_stash_codes.index(Stash(stash_code).itemcode)
    except ValueError:
        LOGGER.error(
            f"Provided STASH code '{stash_code}' not found in UM fieldsfile."
        )

# ===== TO TEST
args = argparse.Namespace(
    subcommand='modify',
    verbose=None,
    silent=None,
    debug=True,
    infile='/g/data/tm70/dm5220/ancil/dietmar/test/qrparm.orog.original',
    outfile='/g/data/tm70/dm5220/ancil/dietmar/test/qrparm.orog.original_modified',
    ncfile='/g/data/tm70/dm5220/ancil/dietmar/test/qrparm.orog.original.nc',
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
    LOGGER.debug(f"{args=}")
    # Get input path
    infile = get_abspath(args.infile)
    LOGGER.debug(f"{infile=}")
    # Get output path
    outfile = get_abspath(args.outfile, checkdir=True)
    LOGGER.debug(f"{outfile=}")
    # Check that options have the right formats
    check_option_formats(args.ufunc, args.stash_codes)
    # Use mule to read the UM file
    LOGGER.info(f"Reading UM file {infile}")
    ff = read_fieldsfile(infile)
    if args.ncfile is not None:
        # Read netCDF file
        ncfile = get_abspath(args.ncfile)
        LOGGER.debug(f"{ncfile=}")
        LOGGER.info(f"Reading netCDF file {ncfile}")
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
    else:
        # Use user-defined function
        LOGGER.info(f"Setting user-defined function to '{args.ufunc}'")
        ufunc = eval(args.ufunc)
    # Copy fieldsfile, to modify it
    ff_new = ff.copy(include_fields=True)
    # If --variables option is specified, select the specified variables
    if args.stash_codes is not None:
        # Get list of stash codes of UM fieldsfile
        ff_stash_codes = get_stash(ff)
        # Get indices of um variables with the selected stash codes
        ff_stash_ind = [get_stash_index(ff_stash_codes,stash_code) for stash_code in args.stash_codes.split()]
    else:
        ff_stash_ind = range(len(ff.fields))
    LOGGER.info(
        "The following UM variables will be modified:\n"
        "\t{}".format('\n\t'.join([Stash(s).__repr__() for s in ff_stash_codes])).expandtabs(9)
    )
    # Modify fieldsfile
    for ind in ff_stash_ind:
        LOGGER.info(f"Modifying {Stash(ff_new.fields[ind].lbuser4)}")
        data = ff_new.fields[ind].get_data()
        if args.ncfile is not None:
            pass
        else:
            data_new = ufunc(data)
        ff_new.fields[ind].set_data_provider(ArrayDataProvider(data_new))
    LOGGER.info(f"Writing UM fieldsfile {outfile}")
    ff_new.to_file(outfile)
    LOGGER.info("Done!")
