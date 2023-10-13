# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

# Script created by Davide Marchegiani (davide.marchegiani@anu.edu.au) at ACCESS-NRI.
# pylint: disable = no-name-in-module
"""Module to define main parser classes."""
import argparse

class ParseFormatter(argparse.RawTextHelpFormatter, argparse.RawDescriptionHelpFormatter):
    """Class to combine argparse Help and Description formatters"""

class SubcommandParser(argparse.ArgumentParser):
    """
    Class to create a parser for the subcommands to have a callback for pre-processing
    """
    def __init__(
            self,
            callback: callable = None,
            **argparse_kwargs
        ) -> argparse.ArgumentParser:
        default_kwargs = {
            'allow_abbrev':False,
            'add_help':False,
        }
        default_kwargs.update(**argparse_kwargs)
        super().__init__(**default_kwargs)
        self.callback = callback
