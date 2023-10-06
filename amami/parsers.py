"""Module to define all argument parsers"""

from typing import Union
import argparse
import sys
import amami

def parse() -> Union[argparse.Namespace, None]:
    """Main parser for CLI usage"""

    # help argument parser
    args_help = argparse.ArgumentParser(
        add_help=False,
        allow_abbrev=False,
        )

    args_help.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="Show this help message and exit.",
    )

    # main parser
    main_parser = argparse.ArgumentParser(
        prog="amami",
        description=amami.__doc__,
        allow_abbrev=False,
        parents=[args_help],
        add_help=False,
    )

    main_parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"{amami.__version__}",
        help="Show program's version number and exit."
    )

    # parser for arguments common to all subcommands
    common_parser = argparse.ArgumentParser(
        add_help=False,
        parents=[args_help],
        allow_abbrev=False,
    )

    common_parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Enable verbose output (-vv for more detailed verbosity).",
    )

    # subparsers for subcommands
    subparses = main_parser.add_subparsers(
        dest="subcommand",
        metavar="command",
    )
    return main_parser.parse_args(sys.argv[1:] if sys.argv[1:] else ["-h"])
