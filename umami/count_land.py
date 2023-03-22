#!/usr/bin/env python

# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

# Script created by Davide Marchegiani at ACCESS-NRI - davide.marchegiani@anu.edu.au

# Count land points in a land_mask UM ancil file

def main(maskFilename):
    STASH_CODE = 30
    mask = read_ancil(maskFilename)
    # Verify that the ancilfile has the correct stash code.
    stash = mask.fields[0].lbuser4
    if stash != STASH_CODE:
        raise QValueError(f"{maskFilename} does not appear to be a valid UM mask file.\n"+\
                f"Stash code should be {STASH_CODE}, but it is {stash}.")
    print(mask.fields[0].get_data().sum())

if __name__ == '__main__':
    import argparse
    # Parse arguments
    description="Count land points in land mask UM ancillary file"
    parser = argparse.ArgumentParser(description=description,
                                    allow_abbrev=False)
    parser.add_argument('maskfile', type=str, help='UM mask file')
    args = parser.parse_args()
    
    # Imports here to improve performance when running with '--help' option
    import os
    import warnings
    warnings.filterwarnings("ignore")
    from umami.ancil_utils import read_ancil
    from umami.quieterrors import QValueError

    maskFilename=os.path.abspath(args.maskfile)
    
    main(maskFilename)

