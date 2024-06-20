# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

"""
Module to control logging for 'amami' package
"""

import logging
import sys

_COLOR_DEBUG = '\033[1;38;2;130;70;160m'
_COLOR_INFO = '\033[1;38;2;0;130;180m'
_COLOR_WARNING = '\033[1;38;2;200;120;50m'
_COLOR_ERROR = '\033[1;38;2;230;50;50m'
_COLOR_END = '\033[0m'


def indent(msg, numtabs):
    """
    Indent a message by a given number of tabs.
    """
    return msg.replace('\r', '').replace('\n', '\n\t'.expandtabs(numtabs))


class CustomConsoleFormatter(logging.Formatter):
    """
    Format messages based on log level.
    """

    def __init__(
        self,
        fmt_debug: str,
        fmt_info: str,
        fmt_warning: str,
        fmt_error: str,
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
        # Call the original formatter class to do the grunt work
        result = logging.Formatter.format(self, record)
        # Restore the original format configured by the user
        self._style._fmt = format_orig
        return result


class CustomLogRecord(logging.LogRecord):
    """
    Custom LogRecord class to add indentation to logging messages.
    """

    def __init__(self, name, level, pathname, lineno,
                 msg, args, exc_info, func=None, sinfo=None, **kwargs):
        TABS = 8
        indented_msg = indent(msg, TABS)
        super().__init__(name, level, pathname, lineno,
                         indented_msg, args, exc_info, func=None,
                         sinfo=None, **kwargs)


def generate_logger():
    """Generate main logger"""
    # Set custom logRecordFactory to apply indentation to logging messages
    logging._logRecordFactory = CustomLogRecord
    # Get logger
    logger = logging.getLogger(__name__)
    # Set handler (console) and custom formatter
    formatter = CustomConsoleFormatter(
        fmt_debug=f"{_COLOR_DEBUG}%(levelname)-7s{_COLOR_END} %(message)s",
        fmt_info=f"{_COLOR_INFO}%(levelname)-7s{_COLOR_END} %(message)s",
        fmt_warning=f"{_COLOR_WARNING}%(levelname)-7s{_COLOR_END} %(message)s",
        fmt_error=f"{_COLOR_ERROR}%(levelname)-7s{_COLOR_END} %(message)s",
    )
    # Create handlers for stdout and stderr
    outhandler = logging.StreamHandler(stream=sys.stdout)
    outhandler.setFormatter(formatter)
    # Add filter to send anything below WARNING to stdout
    outhandler.addFilter(lambda record: record.levelno < logging.WARNING)
    errhandler = logging.StreamHandler(stream=sys.stderr)
    errhandler.setFormatter(formatter)
    # Add filter to send WARNING and ERROR to stderr
    errhandler.addFilter(lambda record: record.levelno >= logging.WARNING)
    # Add handler to logger
    logger.addHandler(outhandler)
    logger.addHandler(errhandler)
    return logger


LOGGER = generate_logger()
