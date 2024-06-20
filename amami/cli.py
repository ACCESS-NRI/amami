# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0
"""
Module to define the entry point for CLI usage of `amami`.
"""

import sys
from importlib import import_module
from amami.parsers import MainParser


class Amami:
    """A class that represents the `amami` application."""

    def __init__(
        self,
        argv: list[str],
    ) -> None:
        # show help when amami is called without arguments or only with supported global option
        parser = MainParser()
        global_options = parser.global_options_parser._option_string_actions.keys()
        if argv[1:]:
            if all(ar in global_options for ar in argv[1:]):
                args = ["-h"] + argv[1:]
            else:
                args = argv[1:]
        else:
            args = ["-h"]
        argv = argv if argv else sys.argv
        self.args = parser.parse_with_callback(args)

    def run_command_main_function(self):
        """
        Calls the `main` function of the amami.commands.<chosen command> module.
        """
        command = getattr(self.args, 'command')
        command_entry_point = getattr(
            import_module(f'amami.commands.{command}'),
            'main',
        )
        # Call 'main' function of chosen command
        command_entry_point(self.args)


def main() -> None:
    """Entry point for CLI usage of `amami`."""
    Amami(sys.argv).run_command_main_function()
