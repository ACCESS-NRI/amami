# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

# Script created by Davide Marchegiani (davide.marchegiani@anu.edu.au) at ACCESS-NRI.

"""Module to define main parser and parser custom classes."""
import argparse
from amami.loggers import LOGGER

class VerboseAction(argparse.Action):
    """Class to enable verbose option '-v/--verbose' to be run as an argparse action"""
    def __init__(self, option_strings, dest, nargs=0, **kwargs):
        if nargs > 0:
            raise ValueError("Arguments not allowed for '-v/--verbose' option.")
        super().__init__(option_strings, dest, nargs=nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        LOGGER.setLevel(20) #logging.INFO
        setattr(namespace, self.dest, True)

class SilentAction(argparse.Action):
    """Class to enable silent option '-s/--silent' to be run as an argparse action"""
    def __init__(self, option_strings, dest, nargs=0, **kwargs):
        if nargs > 0:
            raise ValueError("Arguments not allowed for '-s/--silent' option.")
        super().__init__(option_strings, dest, nargs=nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        import warnings
        warnings.filterwarnings("ignore")
        LOGGER.setLevel(40) #logging.ERROR
        setattr(namespace, self.dest, True)

class DebugAction(argparse.Action):
    """Class to enable debug option '--debug' to be run as an argparse action"""
    def __init__(self, option_strings, dest, nargs=0, **kwargs):
        if nargs > 0:
            raise ValueError("Arguments not allowed for '--debug' option.")
        super().__init__(option_strings, dest, nargs=nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        LOGGER.setLevel(10) #logging.DEBUG
        setattr(namespace, self.dest, True)

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
