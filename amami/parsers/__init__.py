# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

"""Module to define and generate the main parser and run the parse processing."""

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
        if nargs > 0:
            raise ParsingError(
                "Arguments not allowed for '-v/--verbose' option.")
        super().__init__(option_strings, dest, nargs=nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        LOGGER.setLevel(20)  # logging.INFO
        setattr(namespace, self.dest, True)


class SilentAction(argparse.Action):
    """Class to enable silent option '-s/--silent' to be run as an argparse action"""

    def __init__(self, option_strings, dest, nargs=0, **kwargs):
        if nargs > 0:
            raise ParsingError(
                "Arguments not allowed for '-s/--silent' option.")
        super().__init__(option_strings, dest, nargs=nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        import warnings
        warnings.filterwarnings("ignore")
        LOGGER.setLevel(40)  # logging.ERROR
        setattr(namespace, self.dest, True)


class DebugAction(argparse.Action):
    """Class to enable debug option '--debug' to be run as an argparse action"""

    def __init__(self, option_strings, dest, nargs=0, **kwargs):
        if nargs > 0:
            raise ParsingError("Arguments not allowed for '--debug' option.")
        super().__init__(option_strings, dest, nargs=nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        LOGGER.setLevel(10)  # logging.DEBUG
        setattr(namespace, self.dest, True)


class ParseFormatter(argparse.RawTextHelpFormatter, argparse.RawDescriptionHelpFormatter):
    """Class to combine argparse Help and Description formatters"""


class SubcommandParser(argparse.ArgumentParser):
    """
    Class to create a parser for the subcommands to have a callback for pre-processing
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
    Class to extend the functionality of argparse.ArgumentParser and create a custom
    parser that allow preprocessing according to the spefcified command.
    """

    def __init__(self) -> None:
        # Generate help parser
        self.help_parser = self._generate_help_parser()
        # Generate common parser
        self.common_parser = self._generate_common_parser()
        kwargs = {
            "prog": amami.__name__,
            "description": amami.__doc__,
            "parents": [self.help_parser],
            'allow_abbrev': False,
            'formatter_class': ParseFormatter,
            'add_help': False,
        }
        # Generate main parser
        super().__init__(**kwargs)
        # Add arguments to main parser
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
            help="""Show this help message and exit.

""",
        )
        return help_parser

    def _generate_common_parser(self) -> argparse.ArgumentParser:
        # parser for arguments common to all subcommands
        common_parser = argparse.ArgumentParser(
            add_help=False,
            allow_abbrev=False,
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
            help="""Make output completely silent (do not show warnings).
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
        """
        for command in COMMANDS:
            subparser = getattr(
                import_module(f'amami.parsers.{command}_parser'),
                'PARSER',
            )
            self.subparsers.add_parser(
                command,
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

    def parse_and_process(
        self,
        *args,
        **kwargs
    ) -> Union[Callable, None]:
        """
        Parse arguments and preprocess according to the specified command.
        """
        print('parse_and_process_called')
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
