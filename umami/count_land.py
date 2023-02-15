#!/usr/bin/env python

# Count land points in land_mask UM ancil file
# Created by Davide Marchegiani - davide.marchegiani@anu.edu.au
def main(maskFilename):
    STASH_CODE = 30
    mask = read_ancil(maskFilename)
    # Verify that the ancilfile has the correct stash code.
    if mask.fields[0].lbuser4 != STASH_CODE:
        sys.exit(f"{maskFilename} does not appear to be a valid UM mask file.\n"+\
                "Stash code should be {STASH_CODE}, but it is {mask.fields[0].lbuser4}.")
    print(mask.fields[0].get_data().sum())

if __name__ == '__main__':
    import argparse
    import os
    # Parse arguments
    parser = argparse.ArgumentParser(description="Count land points in land mask UM ancillary file")
    parser.add_argument('maskfile', type=str, help='UM mask file')
    args = parser.parse_args()
    maskFilename=os.path.abspath(args.maskfile)
    
    # Imports here to improve performance when running with '--help' option
    import sys
    import warnings
    warnings.filterwarnings("ignore")
    from umami.ancil_utils import read_ancil

    main(maskFilename)

