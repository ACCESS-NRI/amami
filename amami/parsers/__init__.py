# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

"""Module to define and generate the main parser and run the parse processing."""

import argparse
import pkgutil
import amami
from typing import Union, Callable
from importlib import import_module
from rich_argparse import RawTextRichHelpFormatter, RawDescriptionRichHelpFormatter
from amami.loggers import LOGGER, CONSOLE_STDOUT, CONSOLE_STDERR
from amami.exceptions import ParsingError
from amami import commands as amami_commands


# Dynamically declare commands by checking files in the amami/commands folder
# Every command should be paired with its parser, named as <command>_parser.py,
# in the amami/parsers folder.
COMMANDS = [command.name for command in pkgutil.iter_modules(
    amami_commands.__path__)]


class VerboseAction(argparse.Action):
    """Class that enables the '--verbose' option to be run as an argparse action."""

    def __init__(self, option_strings, dest, nargs=0, **kwargs):
        super().__init__(option_strings, dest, nargs=nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        LOGGER.setLevel(20)  # logging.INFO


class SilentAction(argparse.Action):
    """Class that enables the '--silent' option to be run as an argparse action."""

    def __init__(self, option_strings, dest, nargs=0, **kwargs):
        super().__init__(option_strings, dest, nargs=nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        import warnings
        warnings.filterwarnings("ignore")
        LOGGER.setLevel(40)  # logging.ERROR


class DebugAction(argparse.Action):
    """Class that enables the '--debug' option to be run as an argparse action."""

    def __init__(self, option_strings, dest, nargs=0, **kwargs):
        super().__init__(option_strings, dest, nargs=nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        LOGGER.setLevel(10)  # logging.DEBUG


class NoStylingAction(argparse.Action):
    """Class that enables the '--poor' option to be run as an argparse action."""

    def __init__(self, option_strings, dest, nargs=0, **kwargs):
        super().__init__(option_strings, dest, nargs=nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        # Set _color_sistem = None to disable styling and colours for rich consoles
        CONSOLE_STDOUT._color_system = None
        CONSOLE_STDERR._color_system = None
        print('poor action called')


# class ParseFormatter(argparse.RawTextHelpFormatter, argparse.RawDescriptionHelpFormatter):
#     """Class to combine argparse Help and Description formatters"""
class RichParseFormatter(RawTextRichHelpFormatter, RawDescriptionRichHelpFormatter):
    """Class to format argparse Help and Description with rich_argparse"""


# Override RichParseFormatter styles
# for %(prog)s in the usage (e.g. "foo" in "Usage: foo [options]")
RichParseFormatter.styles['argparse.prog'] = 'rgb(145,185,220)'
RichParseFormatter.console = CONSOLE_STDOUT


class ParserWithCallback(argparse.ArgumentParser):
    """
    Class to create a parser that has a callback for parsing pre-processing
    """

    def __init__(
        self,
        callback=None,
        **argparse_kwargs
    ) -> None:
        super().__init__(add_help=False, **argparse_kwargs)
        # If there is no callback in the specific command parser return the known args
        self.callback = callback


class MainParser(argparse.ArgumentParser):
    """
    Class for the main parser.
    The MainParser structure is the following:
    |--- global_options_parser
    |    |  Parser for options valid for both the `amami` program and all its commands
    |    |  (for example the '--help' option: `amami --help` or `amami um2nc --help`)
    |    |
    |    self (MainParser)
    |    |  Parser for options valid only for the `amami` program
    |    |  (for example the '--version' option: `amami --version`)
    |    |
    |    |--- command_parser
    |    |    |  Parser for the `amami` commands
    |    |    |  (for example: `amami um2nc` or `amami modfy`)
    |    |    |
    |    |    |--- common_options_parser
    |    |    |     Parser for options valid for all `amami` commands
    |    |    |     (for example the '--debug' option: `amami um2nc --debug` or `amami modify --debug`)
    |    |    |
    |    |    |--- subparsers
    |    |    |     Parsers for options valid for each specific `amami` command
    |    |    |     One for each command in the `amami.commands` folder (created dynamically)
    """

    def __init__(self) -> None:
        # Generate global options parser
        self.global_options_parser = self._generate_global_parser()
        # Generate MainParser
        self._generate_main_parser()
        # Generate command_parser
        self._generate_command_parser()
        # Generate common_options_parser
        self.common_options_parser = self._generate_common_parser()
        self.generate_subparsers()

    @ staticmethod
    def _generate_global_parser() -> argparse.ArgumentParser:
        """
        Generate the global options parser, for options valid for both the `amami`
        program and its commands.
        """
        # Create parser
        global_parser = argparse.ArgumentParser(
            add_help=False,
            allow_abbrev=False,
            argument_default=argparse.SUPPRESS,
        )

        # Add no colours option
        global_parser.add_argument(
            "--poor", "--nocolours", "--nocolors", "--nostyles",
            action=NoStylingAction,
            help="""Remove colours and styles from output messages.
(Remove the functionality brought by the 'rich' Python package - https://rich.readthedocs.io/en/latest/index.html).

""")
        # Add help option
        global_parser.add_argument(
            "-h",
            "--help",
            action="help",
            help="""Show this help message and exit.

""")
        return global_parser

    def _generate_main_parser(self) -> None:
        """Generate the main parser for options valid only for the `amami` program."""
        super().__init__(
            prog=amami.__name__,
            usage=None,
            description=amami.__doc__,
            parents=[self.global_options_parser],
            formatter_class=RichParseFormatter,
            add_help=False,
            allow_abbrev=False,
        )
        # Add version option
        self.add_argument(
            "-V",
            "--version",
            action="version",
            version=f"{amami.__version__}",
            help="""Show program's version number and exit.

""")

    @staticmethod
    def _generate_common_parser() -> argparse.ArgumentParser:
        """Generate the common options parser, for options valid for all `amami` commands."""
        common_parser = argparse.ArgumentParser(
            add_help=False,
            allow_abbrev=False,
            argument_default=argparse.SUPPRESS,
        )
        # Add mutually exclusive group for verbose, silent and debug options
        _mutual = common_parser.add_mutually_exclusive_group()
        # Add verbose option
        _mutual.add_argument(
            "-v",
            "--verbose",
            dest="verbose",
            action=VerboseAction,
            help="""Enable verbose output.
Cannot be used together with '-s/--silent' or '--debug'.

""",
        )
        # Add silent option
        _mutual.add_argument(
            "-s",
            "--silent",
            dest="silent",
            action=SilentAction,
            help="""Make output completely silent(do not show warnings).
Cannot be used together with '-v/--verbose' or '--debug'.

""",
        )
        # Add debug option
        _mutual.add_argument(
            "--debug",
            dest="debug",
            action=DebugAction,
            help="""Enable debug mode.
Cannot be used together with '-s/--silent' or '-v/--verbose'.

""",
        )
        return common_parser

    def _generate_command_parser(self) -> None:
        # Add subparsers for amami commands
        self.subparsers = self.add_subparsers(
            dest="command",
            metavar="command",
            parser_class=ParserWithCallback,
        )

    def generate_subparsers(self) -> None:
        """
        Function to generate the subparsers for each amami command dynamically.
        Each command parser file needs to be in the amami/parsers folder and the filename
        needs to be in the format '<command>_parser.py'.
        For example, the parser for the 'um2nc' command should be named 'um2nc_parser.py'.
        Each command parser file should have a 'PARSER' variable as an instance of 
        'ParserWithCallback' that represents the command parser.
        """
        for command in COMMANDS:
            subparser = getattr(
                import_module(f'amami.parsers.{command}_parser'),
                'PARSER',
            )
            self.subparsers.add_parser(
                command,
                parents=[
                    self.global_options_parser,
                    self.common_options_parser,
                    subparser,
                ],
                usage=" ".join(subparser.usage.split()),
                description=subparser.description,
                formatter_class=self.formatter_class,
                allow_abbrev=False,
                callback=subparser.callback,  # type: ignore
            )

    def parse_with_callback(
        self,
        *args,
        **kwargs
    ) -> Union[Callable, None]:
        """
        Parse known and unknown arguments and calls a callback on them,
        according to the specified command.
        """
        known_args, unknown_args = self.parse_known_args(*args, **kwargs)
        # Keep track of the command used
        amami.__command__ = known_args.command
        # Unkown args cannot be options (start with '-')
        if unknown_args and any(isoption := [ua.startswith('-') for ua in unknown_args]):
            self.print_usage()
            raise ParsingError(
                f"Option '{unknown_args[isoption.index(True)]}' not supported.")
        elif (callback := self.subparsers.choices[known_args.command].callback):
            return callback(known_args, unknown_args)
        elif unknown_args:
            raise ParsingError(f"Too many arguments: {unknown_args}.")
        else:
            return known_args
