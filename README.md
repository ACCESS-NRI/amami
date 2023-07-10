ACCESS Models Ancillary Manipulation Instruments (UMAMI)

This is a set of tools to handle UM ancillary files.
It is still under development and in a pre-release status, but the functions should still work fine for most files.

The main functions are in the `amami` diretory:
-  `count_land_points.py` --> Counts land points in a UM land/sea mask file
-  `modify.py` --> Modifies an existing UM ancillary file with data from a NetCDF file and creates a new one
-  `regrid.py` --> Regrids a UM ancillary file
-  `um2nc.py` --> Converts a UM file to NetCDF
-  `validate.py` --> Validates a UM ancillary file using Mule

For help on how to use a specific function, run the function with the '--help' flag:
`path/to/modify.py --help`

