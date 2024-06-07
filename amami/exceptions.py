# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

"""
Module to define custom exceptions and exception hooks.
"""


class AmamiError(Exception):
    """Base class for all exceptions in the amami package."""
    pass


class UMError(AmamiError):
    """Exception for Unified Model related errors."""
    pass


class ParsingError(AmamiError):
    """Exception for CLI parsing errors."""
    pass
