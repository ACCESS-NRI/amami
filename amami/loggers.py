# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

"""
Module to control logging for 'amami' package
"""

import logging
import amami
from rich.logging import RichHandler
from rich.console import Console
from rich.theme import Theme

# Override some default rich stylings and add custom ones
custom_rich_theme = Theme({
    # Custom styling for string representation
    "repr.str": "not bold not italic rgb(105,195,65)",
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


class CustomLogRecord(logging.LogRecord):
    """
    Custom LogRecord class to add command to logging messages.
    """

    def __init__(self, name, level, pathname, lineno,
                 msg, args, exc_info, func=None, sinfo=None, **kwargs):
        # Add amami command to message
        command = f" {amami.__command__}" if amami.__command__ else ""
        new_msg = f"[amami_command]{amami.__name__}{command}[/]: {msg}"
        super().__init__(name, level, pathname, lineno,
                         new_msg, args, exc_info, func=None,
                         sinfo=None, **kwargs)


def generate_logger(name, markup=True):
    """Generate custom logger that uses rich formatting"""
    # Set custom logRecordFactory to apply indentation to logging messages
    logging._logRecordFactory = CustomLogRecord  # type: ignore
    # Get logger
    logger = logging.getLogger(name)
    # Create handler for stdout and add filter to send there anything below WARNING
    outhandler = RichHandler(
        console=CONSOLE_STDOUT,
        markup=markup,
        show_time=False,
        show_path=False,
        keywords=[],
    )
    outhandler.addFilter(lambda record: record.levelno < logging.WARNING)
    # Create handler for stderr and add filter to send there anything from WARNING above
    errhandler = RichHandler(
        console=CONSOLE_STDERR,
        markup=markup,
        show_time=False,
        show_path=False,
        keywords=[],
    )
    errhandler.addFilter(lambda record: record.levelno >= logging.WARNING)
    # Add handlers to logger
    logger.addHandler(outhandler)
    logger.addHandler(errhandler)
    return logger


# Create main logger
LOGGER = generate_logger(__name__)
# Create logger without markup formatting (needed mostly for external warnings )
POOR_LOGGER = generate_logger('nomarkup', markup=False)
