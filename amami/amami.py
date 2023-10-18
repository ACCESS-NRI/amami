# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

# Script created by Davide Marchegiani (davide.marchegiani@anu.edu.au) at ACCESS-NRI.


"""
Module to define main class and entry point for CLI usage of `amami`.
"""
import sys
import lazy_loader as lazy
from amami.parsers.main_parser import MainParser
# from amami.core.um2nc import process as um2nc

class Amami:
    """A class that represents the `amami` application."""
    def __init__(
        self,
        argv: list[str],
    ) -> None:
        self.args = MainParser().parse_and_process(
            argv[1:] if argv[1:] else ["-h"]
        )

    def um2nc(self):
        """Main method for `amami um2nc` command."""
        print(self.args)

    def main(self):
        """Main function for `amami`."""
        command = getattr(self.args, 'subcommand')
        method = getattr(self, command)
        method()

def main() -> None:
    """Entry point for CLI usage of `amami`."""
    Amami(sys.argv).main()
