# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

# Script created by Davide Marchegiani (davide.marchegiani@anu.edu.au) at ACCESS-NRI.
# Original script https://gist.github.com/jhazelwo/86124774833c6ab8f973323cb9c7e251

import sys

class QuietError(Exception):
    # All who inherit me shall not traceback, but be spoken of cleanly
    pass

class QValueError(QuietError):
    # Failed to parse data
    pass

class QFixError(QuietError):
    # Failed to parse data
    pass

class QParseError(QuietError):
    # Failed to parse data
    pass

class QFileExistsError(QuietError):
    # Failed to parse data
    pass

def quiet_hook(kind, message, traceback):
    if QuietError in kind.__bases__:
        print(message)
    else:
        sys.__excepthook__(kind, message, traceback)  # Print Error Type, Message and Traceback

sys.excepthook = quiet_hook