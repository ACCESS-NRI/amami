# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0
"""
Script created by Davide Marchegiani (davide.marchegiani@anu.edu.au) at ACCESS-NRI.

Module to define main class and entry point for CLI usage of `amami`.
"""
# pylint: disable=no-member,import-outside-toplevel,too-few-public-methods


import argparse
from amami.core import um2nc


def main():
    parser = argparse.ArgumentParser()

    # TODO: pass in global/logging options, or are these best set in logger config?
    # TODO: versioning to a version.py module?
    # parser.add_argument("-V", "--version",
    #                     version=f"{amami.__version__}",
    #                     help="Show program's version number and exit.")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose",
                       action="store_true",
                       help="Enable verbose output. Cannot be used with '-s/--silent' or '--debug'.")
    group.add_argument("-s", "--silent",
                       action="store_true",
                       help="Make output completely silent (do not show warnings). Cannot be used with '-v/--verbose' or '--debug'.")
    group.add_argument("--debug",
                       action="store_true",
                       help="Enable debug mode. Cannot be used with '-s/--silent' or '-v/--verbose'.")

    subparsers = parser.add_subparsers(dest="subparser_name")

    # configure um2nc subparser
    um2nc_parser = subparsers.add_parser("um2nc")
    um2nc_parser.add_argument("infile",
                              type=str,
                              #metavar="INPUT_FILE",
                              help="Path to the UM fieldsfile for conversion.")

    um2nc_parser.add_argument("-o", "--outfile",
                              required=False,
                              #dest="outfile",
                              type=str,
                              metavar="OUTPUT_FILE",
                              help="Path for converted netCDF output. Defaults to input path with '.nc' suffix.")

    um2nc_parser.add_argument("-f", "--format",
                              default="NETCDF4",
                              choices=["NETCDF4",
                                       "NETCDF4_CLASSIC",
                                       "NETCDF3_CLASSIC",
                                       "NETCDF3_64BIT",
                                       "1",
                                       "2",
                                       "3",
                                       "4",
                                ],
                              help="Specify netCDF format.")

    um2nc_parser.add_argument("-c", "--compression",
                              type=int,
                              default=4,
                              help="Compression level (0=none, 9=max).")
    um2nc_parser.add_argument("--64bit",
                              dest="use64bit",
                              action="store_true",
                              help="Use 64 bit netCDF for input.")
    um2nc_parser.add_argument("--nohist",
                              action="store_true",
                              help="Don't update history attribute.")
    um2nc_parser.add_argument("--simple",
                              action="store_true",
                              help="Use 'simple' variable names of form 'fld_s01i123'.")

    exclusive = um2nc_parser.add_mutually_exclusive_group()
    exclusive.add_argument("--nomask",
                           action="store_true",
                           help=("Don't apply heavyside function mask to pressure level fields. "
                                 "Cannot be used with '--hcrit'."))  # TODO: shorten & rely on exclusion group docs?
    exclusive.add_argument("--hcrit",
                           type=float,
                           default=0.5,
                           help=("Critical value of heavyside function for pressure level masking."
                                 " Cannot be used with '--nomask'"))  # TODO: rely on exclusion groups docs?

    exclusive2 = um2nc_parser.add_mutually_exclusive_group()
    exclusive2.add_argument("--include",
                            dest="include_list",
                            type=int,
                            metavar=("STASH_CODE1", "STASH_CODE2"),
                            nargs="+",
                            help="List of STASH codes to include in the netCDF conversion. Only variables with included STASH codes are converted.")
    exclusive2.add_argument("--exclude",
                            dest="exclude_list",
                            type=int,
                            metavar=("STASH_CODE1", "STASH_CODE2"),
                            nargs="+",
                            help="List of STASH codes to exclude from netCDF conversion. Variables with excluded STASH codes will not be converted.")

    # configure modify subparser
    modify_parser = subparsers.add_parser("modify")

    ns = parser.parse_args()
    print(f"\nnamespace:\n{ns}")

    if ns.subparser_name == "um2nc":
        # general validation
        if ns.format == "NETCDF3_CLASSIC" and ns.use64bit:
            msg = "'NETCDF3_CLASSIC' does not support 64 bit data."
            parser.error(msg)

        um2nc.main(ns.infile,
                   ns.outfile,
                   ns.format,
                   ns.use64bit,
                   ns.include_list,
                   ns.exclude_list,
                   ns.hcrit,
                   ns.nomask,
                   ns.nohist,
                   ns.simple,
                   ns.compression)
    elif ns.subparser_name == "modify":
        parser.exit(-1, "Not implemented!\n")


if __name__ == "__main__":
    main()
