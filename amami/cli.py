# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

# Script created by Davide Marchegiani (davide.marchegiani@anu.edu.au) at ACCESS-NRI.

# pylint: disable = no-name-in-module
"""Entry point module for CLI usage of 'amami'"""
import sys
from amami.parsers.main_parser import MainParser

def main() -> None:
    """Entry point for CLI usage of 'amami'"""
    args = MainParser().parse_and_preprocess(
        sys.argv[1:] if sys.argv[1:] else ["-h"]
    )
    print(args)
