"""Entry point module for CLI usage of 'amami'"""

from amami.parsers import parse

def main() -> None:
    """Entry point function for CLI usage of 'amami'"""
    args = parse()
    print(args)
    