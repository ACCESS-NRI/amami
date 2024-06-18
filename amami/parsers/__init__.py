# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

"""Module to define and generate the main parser and run the parse processing."""

import os
import argparse
import pkgutil
import amami
from typing import Union, Callable
from importlib import import_module
from amami.loggers import LOGGER
from amami.exceptions import ParsingError
from amami import commands as amami_commands


# Dynamically declare commands by checking files in the amami/commands folder
COMMANDS = [command.name for command in pkgutil.iter_modules(
    amami_commands.__path__)]


class VerboseAction(argparse.Action):
    """Class to enable verbose option '-v/--verbose' to be run as an argparse action"""

    def __init__(self, option_strings, dest, nargs=0, **kwargs):
        super().__init__(option_strings, dest, nargs=nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        LOGGER.setLevel(20)  # logging.INFO


class SilentAction(argparse.Action):
    """Class to enable silent option '-s/--silent' to be run as an argparse action"""

    def __init__(self, option_strings, dest, nargs=0, **kwargs):
        super().__init__(option_strings, dest, nargs=nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        import warnings
        warnings.filterwarnings("ignore")
        LOGGER.setLevel(40)  # logging.ERROR


class DebugAction(argparse.Action):
    """Class to enable debug option '--debug' to be run as an argparse action"""

    def __init__(self, option_strings, dest, nargs=0, **kwargs):
        super().__init__(option_strings, dest, nargs=nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        LOGGER.setLevel(10)  # logging.DEBUG


class NoColourAction(argparse.Action):
    """Class to enable option '--nocolours' to be run as an argparse action"""

    def __init__(self, option_strings, dest, nargs=0, **kwargs):
        super().__init__(option_strings, dest, nargs=nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        os.environ["TERM"] = "dumb"


class ParseFormatter(argparse.RawTextHelpFormatter, argparse.RawDescriptionHelpFormatter):
    """Class to combine argparse Help and Description formatters"""


class ParserWithCallback(argparse.ArgumentParser):
    """
    Class to create a parser that has a callback for parsing pre-processing
    """

    def __init__(
        self,
        callback: Union[Callable, None] = None,
        **argparse_kwargs
    ) -> None:
        default_kwargs = {
            'allow_abbrev': False,
            'add_help': False,
        }
        default_kwargs.update(**argparse_kwargs)
        super().__init__(**default_kwargs)
        self.callback = callback


class MainParser(argparse.ArgumentParser):
    """
    Class for the main custom parser. 
    The main parser structure is the following:
    |--- self 
    |    |  Higher level parser for options valid only for the `amami` program 
    |    |  (for example the '--version' option: `amami --version`)
    |    |
    |--- global_parser
    |    |  Parser for options valid for both the `amami` program and all its commands
    |    |  (for example the '--help' option: `amami --help` or `amami um2nc --help`)
    |    |
    |    |--- common_parser
    |    |      Parser for options valid for any `amami` command
    |    |      (for example the '--debug' option: `amami um2nc --debug` or `amami modify --debug`)
    |    |
    |    |--- command_parser
                Parser for options valid for each specific `amami` command



    """

    def __init__(self) -> None:
        # Generate help parser
        self.global_parser = self.generate_global_parser()
        # Generate common parser
        self.common_parser = self._generate_common_parser()
        kwargs = {
            "prog": amami.__name__,
            "description": amami.__doc__,
            "parents": [self.global_parser],
            'allow_abbrev': False,
            'formatter_class': ParseFormatter,
            'add_help': False,
        }
        # Generate main parser
        super().__init__(**kwargs)
        # Add arguments to main parser
        # Version option
        self.add_argument(
            "-V",
            "--version",
            action="version",
            version=f"{amami.__version__}",
            help="""Show program's version number and exit.

"""
        )
        # Add subparsers for subcommands
        self.subparsers = self.add_subparsers(
            dest="subcommand",
            metavar="command",
            parser_class=ParserWithCallback
        )
        self.generate_subparsers()

    @staticmethod
    def generate_global_parser() -> argparse.ArgumentParser:
        """
        Generate the global parser, for options valid for both the `amami` program and its commands
        """
        # Create parser
        parser = argparse.ArgumentParser(
            add_help=False,
            allow_abbrev=False,
            argument_default=argparse.SUPPRESS,
        )

        # Add help option
        parser.add_argument(
            "-h",
            "--help",
            action="help",
            help="""Show this help message and exit.

    """)

        # Add no colours option
        parser.add_argument(
            "--nocolours", "--nocolors", "--nocolour", "--nocolor",
            "--no-colours", "--no-colors", "--no-colour", "--no-color",
            action=NoColourAction,
            help="""Remove colours and styles from output messages.

    """)
        return parser

    def _generate_common_parser(self) -> argparse.ArgumentParser:
        # parser for arguments common to all subcommands
        common_parser = argparse.ArgumentParser(
            add_help=False,
            allow_abbrev=False,
            argument_default=argparse.SUPPRESS,
        )
        _mutual = common_parser.add_mutually_exclusive_group()
        _mutual.add_argument(
            "-v",
            "--verbose",
            dest="verbose",
            action=VerboseAction,
            help="""Enable verbose output.
Cannot be used together with '-s/--silent' or '--debug'.

""",
        )
        _mutual.add_argument(
            "-s",
            "--silent",
            dest="silent",
            action=SilentAction,
            help="""Make output completely silent(do not show warnings).
Cannot be used together with '-v/--verbose' or '--debug'.

""",
        )
        _mutual.add_argument(
            "--debug",
            dest="debug",
            action=DebugAction,
            help="""Enable debug mode.
Cannot be used together with '-s/--silent' or '-v/--verbose'.

""",
        )
        return common_parser

    def generate_subparsers(self) -> None:
        """
        Function to generate the subparsers dynamically, as they are added to the
        amami/parsers folder.
        The parser name need to be in the format `<command>_parser.py`.
        For example, the parser for the `um2nc` command should be named `um2nc_parser.py`.
        """
        for command in COMMANDS:
            subparser = getattr(
                import_module(f'amami.parsers.{command}_parser'),
                'PARSER',
            )
            self.subparsers.add_parser(
                command,
                parents=[
                    self.global_parser,
                    self.common_parser,
                    subparser,
                ],
                usage=" ".join(subparser.usage.split()),
                description=subparser.description,
                formatter_class=ParseFormatter,
                add_help=False,
                callback=subparser.callback,
            )

    def parse_and_process(
        self,
        *args,
        **kwargs
    ) -> Union[Callable, None]:
        """
        Parse arguments and preprocess according to the specified command.
        """
        known_args, unknown_args = self.parse_known_args(*args, **kwargs)
        if known_args.subcommand is not None:
            if (callback := self.subparsers
                    .choices[known_args.subcommand].callback):  # Assignment expression
                return callback(known_args, unknown_args)
            elif unknown_args:
                raise ParsingError(
                    f"Option '{unknown_args[0]}' not supported.")
            else:
                return known_args
        else:
            self.print_usage()
            raise ParsingError(f"Option '{unknown_args[0]}' not supported.")
