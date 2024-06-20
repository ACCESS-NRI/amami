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
        self.args = MainParser().parse_with_callback(
            argv[1:] if argv[1:] else ["-h"]
        )

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
