# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

# Script created by Davide Marchegiani (davide.marchegiani@anu.edu.au) at ACCESS-NRI.

"""Module to define main parser classes."""

import argparse
# from amami.parsers.um2nc_parser import PARSER as um2nc_parser

# SUBPARSERS = {
#     "um2nc": um2nc_parser,
# }

class ParseFormatter(argparse.RawTextHelpFormatter, argparse.RawDescriptionHelpFormatter):
    """Class to combine argparse Help and Description formatters"""

class SubcommandParser(argparse.ArgumentParser):
    """
    Class to create a parser for the subcommands
    """
    def __init__(
            self,
            *args,
            preprocess_fun = None,
            **argparse_kwargs
        ) -> argparse.ArgumentParser:
        default_kwargs = {
            'allow_abbrev':False,
            'add_help':False,
        }
        default_kwargs.update(**argparse_kwargs)
        super().__init__(*args,**default_kwargs)
        self.preprocess_fun = preprocess_fun
