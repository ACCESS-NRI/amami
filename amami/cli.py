"""Entry point module for CLI usage of 'amami'"""
# pylint: disable = no-name-in-module
from amami.parsers import parse

def main() -> None:
    """Entry point function for CLI usage of 'amami'"""
    args = parse()
    print(args)
