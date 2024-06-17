# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

"""
Module to define custom exceptions and exception hooks.
"""
import sys
import traceback
from amami.loggers import LOGGER


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
    """Exception for CLI parsing errors."""
    pass


# Create custom exception hook to customize the exceptions formatting
# via the logging module.
def custom_excepthook(exc_type, exc_value, exc_traceback):
    """Custom excepthook to handle exceptions."""
    if issubclass(exc_type, AmamiError):
        # If the logger is enabled for DEBUG level print the traceback
        if LOGGER.isEnabledFor(10):
            print("*** Traceback (most recent call last) ***\n")
            traceback.print_tb(exc_traceback)
        LOGGER.error("%s", exc_value)
    else:
        sys.__excepthook__(exc_type, exc_value, exc_traceback)


# Assign the custom excepthook to the system excepthook
sys.excepthook = custom_excepthook
