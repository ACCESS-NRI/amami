# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0
"""
Script created by Davide Marchegiani (davide.marchegiani@anu.edu.au) at ACCESS-NRI.

Module to define main class and entry point for CLI usage of `amami`.
"""
# pylint: disable=no-member,import-outside-toplevel,too-few-public-methods

import sys
from amami.parsers.main_parser import MainParser


# FIXME: can the class be replaced by procedural argparse?
#        argparse should clean up & autogenerate arg docs
class Amami:
    """A class that represents the `amami` application."""

    def __init__(self, argv: list[str]):
        self.args = MainParser().parse_and_process(argv[1:] if argv[1:] else ["-h"])

    def run_command(self):
        """Main function for `amami`."""

        # FIXME: dynamic code hides args & calling of the sub commands
        #        consider replacing with argparse subcommand to directly call
        #        processing functions (with keyword args?)
        command = getattr(self.args, "subcommand")
        from importlib import import_module

        mainfun = getattr(
            import_module(f"amami.core.{command}"),
            "main",
        )
        # Call 'main' function of chosen command
        mainfun(self.args)


def main() -> None:
    """Entry point for CLI usage of `amami`."""
    Amami(sys.argv).run_command()
