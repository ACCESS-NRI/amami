# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0
"""
Module to define the settings and classes used for the colouring/styling of output.
"""

from rich.console import Console
from rich.theme import Theme
from rich_argparse import RawTextRichHelpFormatter, RawDescriptionRichHelpFormatter
from rich.logging import RichHandler

# Override some default rich stylings and add custom ones
custom_rich_theme = Theme({
    # Custom styling for string highlight
    "repr.str": "not bold not italic rgb(105,185,65)",
    # Custom styling for url highlight
    'repr.url': 'not bold not italic underline rgb(125,185,105)',
    # Custom styling for DEBUG logging level
    'logging.level.debug': 'bold medium_orchid',
    # Custom styling for INFO logging level
    'logging.level.info': 'bold dodger_blue1',
    # Custom styling for WARNING logging level
    'logging.level.warning': 'bold orange3',
    # Custom styling for ERROR logging level
    'logging.level.error': 'bold rgb(190,40,40)',
    # Custom styling for amami <command> in logs
    'amami_command': 'bold italic rgb(145,185,220)',
})
# Create consoles for rich output
CONSOLE_STDOUT = Console(theme=custom_rich_theme)
CONSOLE_STDERR = Console(theme=custom_rich_theme, stderr=True)


def generate_rich_handler(stdout=True, markup=True):
    """
    Generate a RichHandler with the given settings.
    """
    return RichHandler(
        console=CONSOLE_STDOUT if stdout else CONSOLE_STDERR,
        markup=markup,
        show_time=False,
        show_path=False,
        keywords=[],
    )


class RichParseFormatter(RawTextRichHelpFormatter, RawDescriptionRichHelpFormatter):
    """
    Class to format argparse Help and Description using the raw help and description classes from rich_argparse
    """


# Set RichParseFormatter console
RichParseFormatter.console = CONSOLE_STDOUT
# Add/Override RichParseFormatter styles
# for %(prog)s in the usage (e.g. "foo" in "Usage: foo [options]")
RichParseFormatter.styles['argparse.prog'] = 'rgb(145,185,220)'
RichParseFormatter.styles['argparse.link'] = RichParseFormatter.console.get_style(
    'repr.url')
# Overwrite RichParseFormatter highlights rules
# # Clear highlights rules
# RichParseFormatter.highlights.clear()
RichParseFormatter.highlights = [
    # Highlight options (prefixed with '--' or '-')
    '(?:^|[\\s[({`])(?P<args>-{1,2}[\\w]+[\\w-]*)',
    # '(?:^|\\s)(?P<args>-{1,2}[\\w]+[\\w-]*)',
    # Highlight text wrapped with backticks (`...`)
    '`(?P<syntax>[^`]*)`',
    # Highlight 'amami'/'AMAMI'
    # '(?i)(?:^|\\s)(?P<prog>amami)(?:$|\\s)',
    # Highlight 'links'
    '(?:^|\\s)(?P<link>http[s]?:[\\\\/]{2}[^\\s]*[\\w\\\\/_-])',
]
