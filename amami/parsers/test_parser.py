# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

"""
Test command parser to be deleted
"""

from amami.parsers import SubcommandParser


DESCRIPTION = """
Test
"""

USAGE = """
amami test
"""

# Create parser
PARSER = SubcommandParser(
    usage=USAGE,
    description=DESCRIPTION,
)
