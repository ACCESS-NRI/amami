# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

"""
Test command to be deleted
"""

from amami.loggers import LOGGER


def main(args):
    LOGGER.debug('Test debug')
    LOGGER.info('Test info')
    LOGGER.warning('Test warning')
    LOGGER.error('Test error')
