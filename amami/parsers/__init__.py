# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

# Script created by Davide Marchegiani (davide.marchegiani@anu.edu.au) at ACCESS-NRI.

"""Module to define all argument parsers"""

from typing import Union
import argparse
import dataclasses
import amami
from amami.parsers.um2nc_parser import Um2ncParser

class ParseFormatter(argparse.RawTextHelpFormatter, argparse.RawDescriptionHelpFormatter):
    """Class to combine argparse Help and Description formatters"""

class ExtendedParser(argparse.ArgumentParser):
    """
    Class to extend the functionality of argparse.ArgumentParser and create a custom
    parse_args function that allow preprocessing according to the spefcified command.
    """
    def __init__(self,*args,**kwargs):
        default_kwargs = {
            'allow_abbrev':False,
            'formatter_class':ParseFormatter,
            'add_help':False,
        }
        default_kwargs.update(kwargs)
        super().__init__(*args,**default_kwargs)

    def parse_and_preprocess(self,*args,**kwargs) -> argparse.Namespace:
        """
        Parse arguments and preprocess according to the specified command.
        """
        known_args, unknown_args = self.parse_known_args(*args,**kwargs)
        return (known_args, unknown_args)


@dataclasses.dataclass
class MainParser():
    """Class to define main parser for the `amami` command"""

    # help argument parser
    _help_parser = argparse.ArgumentParser(
        add_help=False,
        allow_abbrev=False,
    )

    _help_parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="Show this help message and exit.",
    )

    # main parser
    PARSER = argparse.ArgumentParser(
        prog="amami",
        description=amami.__doc__,
        allow_abbrev=False,
        parents=[_help_parser],
        formatter_class=ParseFormatter,
        add_help=False,
    )

    PARSER.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"{amami.__version__}",
        help="Show program's version number and exit."
    )

    # parser for arguments common to all subcommands
    _common_parser = argparse.ArgumentParser(
        add_help=False,
        allow_abbrev=False,
    )

    _common_parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Enable verbose output (-vv for more detailed verbosity).",
    )

    # subparsers for subcommands
    _subparsers = PARSER.add_subparsers(
        dest="subcommand",
        metavar="command",
    )
    # parser for 'amami um2nc'
    _subparsers.add_parser(
        "um2nc",
        parents=[
            _help_parser,
            _common_parser,
            Um2ncParser.PARSER,
        ],
        usage=" ".join(Um2ncParser.USAGE.split()),
        description=Um2ncParser.DESCRIPTION,
        formatter_class=ParseFormatter,
        add_help=False,
    )
