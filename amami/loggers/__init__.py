# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

# pylint: disable = protected-access, no-name-in-module
"""
Module to control logging for 'amami' package
"""

from types import MethodType
from amami import lazy_import
logging = lazy_import("logging")
sys = lazy_import("sys")

def new_error(self, msg, *args, **kwargs):
    """
    Extend logging.error method to exit automatically
    after logging the message.
    """
    if self.isEnabledFor(logging.ERROR):
        sys.exit(self._log(logging.ERROR, msg, args, **kwargs))

def new_critical(self, msg, *args, **kwargs):
    """
    Extend logging.critical method to exit automatically
    after logging the message.
    """
    if self.isEnabledFor(logging.CRITICAL):
        sys.exit(self._log(logging.CRITICAL, msg, args, **kwargs))

class CustomConsoleFormatter(logging.Formatter):
    """
    Format messages based on log level.
    """
    def __init__(
            self,
            fmt_debug:str=None,
            fmt_info:str=None,
            fmt_warning:str=None,
            fmt_error:str=None,
            fmt_critical=None,
            **formatter_kwargs,
        ) -> None:
        default_kwargs = {
            'fmt': '%(levelname)s: %(message)s',
            'style': '%',
            'datefmt': None,
        }
        default_kwargs.update(formatter_kwargs)
        super().__init__(**default_kwargs)
        self._fmt_debug = fmt_debug
        self._fmt_info = fmt_info
        self._fmt_warning = fmt_warning
        self._fmt_error = fmt_error
        self._fmt_critical = fmt_critical

    def format(self, record):
        """
        Set custom logging formats based on the log level
        """
        # Save the original format configured by the user
        format_orig = self._style._fmt
        # Replace the original format with one customized by logging level
        if (record.levelno == logging.DEBUG) and (self._fmt_debug is not None):
            self._style._fmt = self._fmt_debug
        elif (record.levelno == logging.INFO) and (self._fmt_info is not None):
            self._style._fmt = self._fmt_info
        elif (record.levelno == logging.WARNING) and (self._fmt_warning is not None):
            self._style._fmt = self._fmt_warning
        elif (record.levelno == logging.ERROR) and (self._fmt_error is not None):
            self._style._fmt = self._fmt_error
        elif (record.levelno == logging.CRITICAL) and (self._fmt_critical is not None):
            self._style._fmt = self._fmt_critical
        # Call the original formatter class to do the grunt work
        result = logging.Formatter.format(self, record)
        # Restore the original format configured by the user
        self._style._fmt = format_orig
        return result

def generate_logger():
    """Generate main logger"""
    # Get logger
    logger = logging.getLogger('amami')
    # Set basic level
    logger.setLevel(logging.WARNING)
    # Set handler (console) and custom formatter
    handler = logging.StreamHandler()
    formatter = CustomConsoleFormatter(
        fmt_info="%(message)s",
    )
    handler.setFormatter(formatter)
    # Add handler to logger
    logger.addHandler(handler)
    # Set custom error and critical methods
    logger.error = MethodType(new_error,logger)
    logger.critical = MethodType(new_critical,logger)
    return logger

LOGGER = generate_logger()
