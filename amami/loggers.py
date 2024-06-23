# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

"""
Module to control logging for 'amami' package
"""

import logging
import amami
from amami.rich_amami import generate_rich_handler


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


def generate_logger(name, outhandler, errhandler):
    """Generate custom logger that uses rich formatting"""
    # Set custom logRecordFactory to apply indentation to logging messages
    logging._logRecordFactory = CustomLogRecord  # type: ignore
    # Get logger
    logger = logging.getLogger(name)
    # Create handler for stdout and add filter to send there anything below WARNING
    outhandler.addFilter(lambda record: record.levelno < logging.WARNING)
    # Create handler for stderr and add filter to send there anything from WARNING above
    errhandler.addFilter(lambda record: record.levelno >= logging.WARNING)
    # Add handlers to logger
    logger.addHandler(outhandler)
    logger.addHandler(errhandler)
    return logger


# Create main logger
LOGGER = generate_logger(
    name=__name__,
    outhandler=generate_rich_handler(markup=True),
    errhandler=generate_rich_handler(stdout=False, markup=True)
)
# Create logger without markup formatting (needed mostly for external warnings )
POOR_LOGGER = generate_logger(
    name='nomarkup',
    outhandler=generate_rich_handler(markup=False),
    errhandler=generate_rich_handler(stdout=False, markup=False)
)
