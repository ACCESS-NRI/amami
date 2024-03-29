# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

"""
Module to define the parser for the `um2nc` subcommand.

Script created by Davide Marchegiani (davide.marchegiani@anu.edu.au) at ACCESS-NRI.
"""

from typing import List
import argparse
from amami.parsers.core import SubcommandParser
from amami.loggers import LOGGER

DESCRIPTION="""
Convert UM fieldsfile to netCDF.
For more information about UM fieldsfiles, please refer to"""\
""" https://code.metoffice.gov.uk/doc/um/latest/papers/umdp_F03.pdf"""\
""" (MOSRS account needed).

Examples
`um2nc [-i] INPUT_FILE`
Converts INPUT_FILE to netCDF and saves the output as INPUT_FILE.nc

`um2nc [-i] INPUT_FILE [-o] OUTPUT_FILE -v`
Converts INPUT_FILE to netCDF and saves the output as OUTPUT_FILE. Verbosity is enabled.

`um2nc [-i] INPUT_FILE [-o] OUTPUT_FILE --format NETCDF3_CLASSIC --simple`
Converts INPUT_FILE to a NETCDF3 CLASSIC netCDF, using "simple" variable names"""\
""" (in the form "fld_s01i123"), and saves the output as OUTPUT_FILE.
"""

USAGE="""
amami um2nc [-h] [i] INPUT_FILE [[-o] OUTPUT_FILE] [-v|-s|--debug] 
[--format {NETCDF4,NETCDF4_CLASSIC,NETCDF3_CLASSIC,NETCDF3_64BIT,1,2,3,4}] 
[-c COMPRESSION] [--64] [--nomask|--hcrit HCRIT] [--nohist] [--simple] 
[--include STASH_CODE1 [STASH_CODE2 ...]|--exclude STASH_CODE1 [STASH_CODE2 ...]]
"""

def check_input_output(
        known_args: argparse.Namespace,
        unknown_args: List[str]
    ) -> argparse.Namespace:
    """
    Preprocessing for `um2nc` parser.
    Checks optional and positional parameters to understand input and output, 
    and set default output if not provided.
    """

    # Convert known_args to dict to be able to modify them
    known_args_dict = vars(known_args)
    # Check optional and positional parameters to determine input and output paths.
    if (
        len(unknown_args) > 2
        ) or (
        (None not in [known_args_dict['infile'],known_args_dict['outfile']])
        and
        (len(unknown_args) > 0)
        ) or (
        ((known_args_dict['infile'] is None) ^ (known_args_dict['outfile'] is None))
        and
        (len(unknown_args) > 1)
        ):
        LOGGER.error(f"Too many arguments.\n\nusage: {' '.join(USAGE.split())}")
    elif (
        (known_args_dict['infile'] is None) and (len(unknown_args) == 0)
        ):
        LOGGER.error(f"No input file provided.\n\nusage: {' '.join(USAGE.split())}")
    elif known_args_dict['infile'] is None:
        known_args_dict['infile'] = unknown_args[0]
        if known_args_dict['outfile'] is None:
            if len(unknown_args) == 2:
                known_args_dict['outfile'] = unknown_args[1]
            else:
                known_args_dict['outfile'] = f"{known_args_dict['infile']}.nc"
    elif known_args_dict['outfile'] is None:
        if len(unknown_args) == 1:
            known_args_dict['outfile'] = unknown_args[0]
        else:
            known_args_dict['outfile'] = f"{known_args_dict['infile']}.nc"
    return argparse.Namespace(**known_args_dict)
#===== pylint: disable = no-value-for-parameter
# Create parser
PARSER=SubcommandParser(
    usage=USAGE,
    description=DESCRIPTION,
    callback=check_input_output,
)
#===== pylint: enable = no-value-for-parameter
# Add arguments
PARSER.add_argument(
    '-i', '--input',
    dest='infile',
    required=False,
    type=str,
    metavar="INPUT_FILE",
    help="""UM input file path.
Note: Can be also inserted as a positional argument."""
)
PARSER.add_argument(
    '-o', '--output',
    required=False,
    dest='outfile',
    type=str,
    metavar="OUTPUT_FILE",
    help="""Converted netCDF output file path.
If not provided, the output will be generated by appending '.nc' to the input file.
Note: Can be also inserted as a positional argument."""
)
PARSER.add_argument(
    '-f', '--format',
    dest='format',
    required=False,
    type=str.upper,
    default='NETCDF4',
    choices=['NETCDF4', 'NETCDF4_CLASSIC', 'NETCDF3_CLASSIC', 'NETCDF3_64BIT', '1','2','3','4'],
    help="""Specify netCDF format among 1 ('NETCDF4'), 2 ('NETCDF4_CLASSIC'),"""\
""" 3 ('NETCDF3_CLASSIC') or 4 ('NETCDF3_64BIT').
Either numbers or strings are accepted. 
Default: 1 ('NETCDF4')."""
)
PARSER.add_argument(
    '-c', '--compression',
    dest='compression',
    required=False,
    type=int,
    default=4,
    help="""Compression level (0=none, 9=max).
Default 4."""
)
PARSER.add_argument(
    '--64bit',
    dest='use64bit',
    action='store_true',
    help='Use 64 bit netCDF for 64 bit input.'
)
PARSER.add_argument(
    '--nohist',
    dest='nohist',
    action='store_true',
    help="Don't update history attribute."
)
PARSER.add_argument(
    '--simple',
    dest='simple',
    action='store_true',
    help="Use 'simple' variable names of form 'fld_s01i123'."
)
mutual1 = PARSER.add_mutually_exclusive_group()
mutual1.add_argument(
    '--nomask',
    dest='nomask',
    action='store_true',
    help="""Don't apply heavyside function mask to pressure level fields.
Cannot be used together with '--hcrit'."""
)
mutual1.add_argument(
    '--hcrit',
    dest='hcrit',
    type=float,
    default=0.5,
    help="""Critical value of heavyside function for pressure level masking.
Default: 0.5.
Cannot be used together with '--nomask'."""
)
mutual2 = PARSER.add_mutually_exclusive_group()
mutual2.add_argument(
    '--include',
    dest='include_list',
    type=int,
    nargs = '+',
    help = """List of stash codes to include in the netCDF conversion.
Only the variables with the included stash codes will be converted.
Cannot be used together with '--exclude'."""
)
mutual2.add_argument(
    '--exclude',
    dest='exclude_list',
    type=int,
    nargs = '+',
    help = """List of stash codes to exclude from the netCDF conversion.
The variables with the excluded stash codes will not be converted.
Cannot be used together with '--include'."""
)
