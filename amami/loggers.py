# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

"""
Module to control logging for 'amami' package
"""

import traceback
import logging
from types import MethodType
import warnings

_COLOR_DEBUG = '\033[1;38;2;130;70;160m'
_COLOR_INFO = '\033[1;38;2;0;130;180m'
_COLOR_WARNING = '\033[1;38;2;200;120;50m'
_COLOR_ERROR = '\033[1;38;2;230;50;50m'
_COLOR_CRITICAL = '\033[1;38;2;255;10;10m'
_COLOR_END = '\033[0m'


def indent(msg, numtabs):
    """
    Indent a message by a given number of tabs.
    """
    return msg.replace('\n','\n\t'.expandtabs(numtabs))


def custom_debug(self, msg, *args, **kwargs):
    """
    Extend logging.debug method to add indentation to logging messages.
    """
    if self.isEnabledFor(logging.DEBUG):
        msg = indent(msg, self.TABS)
        self._log(
            logging.DEBUG, 
            msg,
            args, 
            **kwargs
        )


def custom_info(self, msg, *args, **kwargs):
    """
    Extend logging.info method to add indentation to logging messages.
    """
    if self.isEnabledFor(logging.INFO):
        msg = indent(msg, self.TABS)
        self._log(
            logging.INFO, 
            msg,
            args, 
            **kwargs
        )


def custom_warning(self, msg, *args, **kwargs):
    """
    Extend logging.warning method to add indentation to logging messages.
    """
    if self.isEnabledFor(logging.WARNING):
        msg = indent(msg, self.TABS)
        self._log(
            logging.WARNING, 
            msg,
            args, 
            **kwargs
        )


def custom_error(self, msg, *args, **kwargs):
    """
    Extend logging.error method to add indentation to logging messages,
    add traceback if DEBUG level is active,
    and automatically exit after the message is logged.
    """
    msg = indent(msg, self.TABS)
    if ((self.isEnabledFor(logging.DEBUG)) and
            (traceback.format_exc() != "NoneType: None\n")):
        msg += "\n" + traceback.format_exc()
        self._log(logging.ERROR, msg, args, **kwargs)


def custom_critical(self, msg, *args, **kwargs):
    """
    Extend logging.critical method to add indentation to logging messages,
    add traceback if DEBUG level is active,
    and automatically exit after the message is logged.
    """
    msg = indent(msg, self.TABS)
    if self.isEnabledFor(logging.DEBUG):
        msg += "\n" + indent(traceback.format_exc(), self.TABS)
        self._log(logging.CRITICAL, msg, args, **kwargs)


class CustomConsoleFormatter(logging.Formatter):
    """
    Format messages based on log level.
    """
    def __init__(
            self,
            fmt_debug: str=None,
            fmt_info: str=None,
            fmt_warning: str=None,
            fmt_error: str=None,
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
    formatter = CustomConsoleFormatter(
        fmt_debug=f"{_COLOR_DEBUG}%(levelname)-8s{_COLOR_END} %(message)s",
        fmt_info=f"{_COLOR_INFO}%(levelname)-8s{_COLOR_END} %(message)s",
        fmt_warning=f"{_COLOR_WARNING}%(levelname)-8s{_COLOR_END} %(message)s",
        fmt_error=f"{_COLOR_ERROR}%(levelname)-8s{_COLOR_END} %(message)s",
        fmt_critical=f"{_COLOR_CRITICAL}%(levelname)-8s{_COLOR_END} %(message)s",
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    # Add handler to logger
    logger.addHandler(handler)
    # Set custom logging methods
    logger.debug = MethodType(custom_debug,logger)
    logger.info = MethodType(custom_info,logger)
    logger.warning = MethodType(custom_warning,logger)
    logger.error = MethodType(custom_error,logger)
    logger.critical = MethodType(custom_critical,logger)
    return logger


LOGGER = generate_logger()
# Set tabs space for logging indentation
setattr(LOGGER,"TABS",9)


# Make warnings use LOGGER.warning instead of the default format
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
    LOGGER.warning(
        f"{filename}:{lineno} - {message}".replace('\n','\n\t').expandtabs(LOGGER.TABS)
    )


warnings.showwarning = external_warning_formatting
