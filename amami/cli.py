# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

# Script created by Davide Marchegiani (davide.marchegiani@anu.edu.au) at ACCESS-NRI.

"""Entry point module for CLI usage of 'amami'"""
# pylint: disable = no-name-in-module
import sys
from amami.parsers import MainParser

def main() -> None:
    """Entry point function for CLI usage of 'amami'"""
    args = MainParser.PARSER.parse_known_args(
        sys.argv[1:] if sys.argv[1:] else ["-h"]
    )
    print(args)