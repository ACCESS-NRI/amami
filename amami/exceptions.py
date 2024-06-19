# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

"""
Module to define custom exceptions, custom exception hooks and
custom warning formatting.
"""

import sys
import traceback
import warnings
from amami.loggers import LOGGER, POOR_LOGGER


class AmamiError(Exception):
    """Base class for all exceptions in the amami package."""
    pass


class UMError(AmamiError):
    """Exception for Unified Model related errors."""
    pass


class ParsingError(AmamiError):
    """Exception for CLI parsing errors."""
    pass


class AmamiNotImplementedError(AmamiError):
    """Exception for the amami NotImplementedError."""
    pass


# Create custom exception hook to customize the exceptions formatting
# via the logging module.
def custom_excepthook(exc_type, exc_value, exc_traceback):
    """Custom excepthook to handle exceptions."""
    if issubclass(exc_type, AmamiError):
        # If the logger is enabled for DEBUG level print the traceback
        if LOGGER.isEnabledFor(10):
            print("\n*** Traceback (most recent call last) ***\n", file=sys.stderr)
            traceback.print_tb(exc_traceback)
        LOGGER.error("%s", exc_value)
    else:
        sys.__excepthook__(exc_type, exc_value, exc_traceback)


# Assign the custom excepthook to the system excepthook
sys.excepthook = custom_excepthook


# Make external warnings (not raised by amami) use LOGGER.warning
# instead of the default format
def external_warning_formatting(
    message,
    category,
    filename,
    lineno,
    file=None,
    line=None
):
    """
    Custom formatting for warnings, to use 'LOGGER.warning'
    and keep proper indentation.
    """
    POOR_LOGGER.warning(
        "%s:%s - %s",
        filename,
        lineno,
        message,
    )


warnings.showwarning = external_warning_formatting
