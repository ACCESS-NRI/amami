# UMAMI

<!-- [![pre-commit](https://github.com/dougiesquire/morte/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/dougiesquire/morte/actions/workflows/pre-commit.yml)
[![tests](https://github.com/dougiesquire/morte/actions/workflows/tests.yml/badge.svg)](https://github.com/dougiesquire/morte/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/dougiesquire/morte/branch/main/graph/badge.svg?token=N0XB8OZ2AE)](https://codecov.io/gh/dougiesquire/morte)
[![License: MIT](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://github.com/dougiesquire/morte/blob/master/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black) -->

Unified Model Ancillary Manipulation Instruments (UMAMI)

This is a set of tools to handle UM ancillary files.
It is still in a pre-release status, but the functions should still work fine for most files.

The main functions are in the `umami/umami` diretory:
-  count_land_points.py --> Counts land points in a UM land/sea mask file
-  modify.py --> Modifies an existing UM ancillary file with data from a NetCDF file and creates a new one
-  regrid.py --> Regrids a UM ancillary file
-  um2nc.py --> Converts a UM file to NetCDF
-  validate.py --> Validates a UM ancillary file using Mule

For help on how to use a specific function, run the function with the '--help' flag:
`path/to/modify.py --help`

