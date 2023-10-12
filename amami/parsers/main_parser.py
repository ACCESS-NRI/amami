# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

# Script created by Davide Marchegiani (davide.marchegiani@anu.edu.au) at ACCESS-NRI.

"""Module to define main parser class."""

import argparse
import amami
from amami.parsers.core import ParseFormatter
from amami.parsers.um2nc_parser import PARSER as um2nc_parser

class MainParser(argparse.ArgumentParser):
    """
    Class to extend the functionality of argparse.ArgumentParser and create a custom
    parser that allow preprocessing according to the spefcified command.
    """
    def __init__(self) -> None:
        # Generate help parser
        self.help_parser = self._generate_help_parser()
        # Generate common parser
        self.common_parser = self._generate_common_parser()
        kwargs = {
            "prog":"amami",
            "description":amami.__doc__,
            "parents":[self.help_parser],
            'allow_abbrev':False,
            'formatter_class':ParseFormatter,
            'add_help':False,
        }
        # Generate main parser
        super().__init__(**kwargs)
        # Add arguments to main parser
        self.add_argument(
            "-V",
            "--version",
            action="version",
            version=f"{amami.__version__}",
            help="Show program's version number and exit."
        )
        # Add subparsers for subcommands
        self.subparsers = self.add_subparsers(
            dest="subcommand",
            metavar="command",
        )
        self.subparsers._parser_class = argparse.ArgumentParser
        # Parser for 'amami um2nc'
        self.subparsers.add_parser(
            "um2nc",
            parents=[
                self.help_parser,
                self.common_parser,
                um2nc_parser,
            ],
            usage=" ".join(um2nc_parser.usage.split()),
            description=um2nc_parser.description,
            formatter_class=ParseFormatter,
            add_help=False,
        )

    def _generate_help_parser(self) -> argparse.ArgumentParser:
        # help argument parser
        help_parser = argparse.ArgumentParser(
            add_help=False,
            allow_abbrev=False,
        )

        help_parser.add_argument(
            "-h",
            "--help",
            action="help",
            default=argparse.SUPPRESS,
            help="Show this help message and exit.",
        )
        return help_parser

    def _generate_common_parser(self) -> argparse.ArgumentParser:
        # parser for arguments common to all subcommands
        common_parser = argparse.ArgumentParser(
            add_help=False,
            allow_abbrev=False,
        )

        common_parser.add_argument(
            "-v",
            "--verbose",
            action="count",
            default=0,
            help="Enable verbose output (-vv for more detailed verbosity).",
        )
        return common_parser

    def parse_and_preprocess(self,*args,**kwargs) -> argparse.Namespace:
        """
        Parse arguments and preprocess according to the specified command.
        """
        return self.parse_known_args(*args,**kwargs)
        # known_args, unknown_args = self.parse_known_args(*args,**kwargs)
        # if known_args.subcommand == 'um2nc':
        #     self.
        # return (known_args, unknown_args)

    # def generate_subparsers(self) -> list[argparse.ArgumentParser]:
    #     """Function to generate the subparsers for different subcommands"""
    #     self.subparsers = dict()
    #     for subcmd in SUBCOMMANDS:
    #         self.subparsers[subcmd] = self.add_parser(
    #             command,
    #             parents=[
    #                 _help_parser,
    #                 _common_parser,
    #                 Um2ncParser.PARSER,
    #             ],
    #             usage=" ".join(Um2ncParser.USAGE.split()),
    #             description=Um2ncParser.DESCRIPTION,
    #             formatter_class=ParseFormatter,
    #             add_help=False,
    #         )