# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

# Script created by Davide Marchegiani (davide.marchegiani@anu.edu.au) at ACCESS-NRI.

# pylint: disable = no-member
"""Module to define main parser class."""

import argparse
import amami
from amami.parsers.core import ParseFormatter, SubcommandParser
from amami.parsers.um2nc_parser import PARSER as um2nc_parser

SUBPARSERS = {
    "um2nc": um2nc_parser,
}

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
            "prog":amami.__name__,
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
            parser_class=SubcommandParser
        )
        self.generate_subparsers()

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

    def parse_and_process(self,*args,**kwargs) -> argparse.Namespace:
        """
        Parse arguments and preprocess according to the specified command.
        """
        known_args, unknown_args = self.parse_known_args(*args,**kwargs)
        callback = self.subparsers.choices[known_args.subcommand].callback
        if callback:
            return callback(known_args, unknown_args)
        self.parse_args(*args,**kwargs)

    def generate_subparsers(self) -> None:
        """Function to generate the subparsers for different subcommands"""
        for subcmd,subparser in SUBPARSERS.items():
            self.subparsers.add_parser(
                subcmd,
                parents=[
                    self.help_parser,
                    self.common_parser,
                    subparser,
                ],
                usage=" ".join(subparser.usage.split()),
                description=subparser.description,
                formatter_class=ParseFormatter,
                add_help=False,
                callback=subparser.callback,
            )
