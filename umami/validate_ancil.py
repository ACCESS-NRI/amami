#!/usr/bin/env python

# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

# Script created by Davide Marchegiani (davide.marchegiani@anu.edu.au) at ACCESS-NRI.

# Validate a UM ancillary file

def main(ancilFilename,fix,inplace,outFilename):
    ancilFilename = os.path.abspath(ancilFilename)
    ancilFile = read_ancil(ancilFilename)
    outFile = validate(ancilFile,fix=fix)
    if outFile is not None:
        if inplace:
            outFilename = ancilFilename
        elif outFilename is None:
            outFilename = ancilFilename + '_fixed'
        else:
            outFilename = os.path.abspath(outFilename)
        outFile.to_file(outFilename)
        print(f"Fixing completed! Written '{outFilename}' to disk.")
    else:
        print(f"'{ancilFilename}' is a valid ancillary file!")

if __name__ == '__main__':
    import argparse
    # Parse arguments
    parser = argparse.ArgumentParser(description="Validate UM ancillary file.",allow_abbrev=False)
    parser.add_argument('-i', '--input', dest='ancilfile', type=str,
                        help='UM ancillary input file.')
    parser.add_argument('-o', '--output', dest='outputfile', type=str,
                        help="If used with the '--fix' option active, specify the output file name.")
    parser.add_argument('--fix', dest='fix', action='store_true', 
        help="Try to fix any validation error and write a new file to disk. "+\
            "Use the '-o' option to specify the output file name. "+\
            "Use the '--inplace' option to modify the input file in place. "+\
            "Alternatively, the output file will have '_fixed' appended to the input file name.")
    parser.add_argument('--inplace', dest='inplace', action='store_true', 
        help="If used with the '--fix' option active, write the file in place instead of creating a new one.")
    parser.add_argument('others', nargs=argparse.REMAINDER)
    args = parser.parse_args()

    # Imports here to improve performance when running with '--help' option
    import warnings
    import os
    warnings.filterwarnings("ignore")
    from umami.ancil_utils.validation_tools import validate
    from umami.ancil_utils import read_ancil
    from umami.quieterrors import QParseError

    ancilFilename = args.ancilfile
    fix = args.fix
    inplace = args.inplace
    others=args.others
    outFilename = args.outputfile

    if ancilFilename is None:
        if others is not None:
            if len(others)==1:
                ancilFilename = others[0]
            elif len(others)>1:
                for opt in ('--fix','--inplace','-o','--output'):
                    if opt in others:
                        raise QParseError("Please place any option before input ancillary file.")
                    raise QParseError("Too many arguments.")
        else:
            raise QParseError("The input ancillary file is required.")
    # Consistency with options
    if not fix:
        if inplace:
            raise QParseError("The '--inplace' option can only be used in conjuction with the '--fix' option.")
        elif outFilename is not None:
            raise QParseError("The '-o/--output' option can only be used in conjuction with the '--fix' option.")
    elif inplace and outFilename is not None:
        raise QParseError("The '-o/--output' and '--inplace' options are mutually exclusive.")
            
    main(ancilFilename,fix,inplace,outFilename)
