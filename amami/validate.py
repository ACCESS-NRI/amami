#!/usr/bin/env python3

# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

# Script created by Davide Marchegiani (davide.marchegiani@anu.edu.au) at ACCESS-NRI.

# Validate a UM file

def main(inputFilename,fix,inplace,outFilename):
    inputFilename = os.path.abspath(inputFilename)
    inputFile = read_fieldsfile(inputFilename,check_ancil=False)
    outFile = validate(inputFile,fix=fix)
    if outFile is not None:
        if inplace:
            outFilename = inputFilename
        elif outFilename is None:
            outFilename = inputFilename + '_fixed'
        else:
            outFilename = os.path.abspath(outFilename)
        outFile.to_file(outFilename)
        print(f"Fixing completed! Written '{outFilename}' to disk.")
    else:
        print(f"'{inputFilename}' is a valid UM file!")

if __name__ == '__main__':
    import argparse
    # Parse arguments
    parser = argparse.ArgumentParser(description="Validate UM ancillary file.",allow_abbrev=False)
    parser.add_argument('-i', '--input', dest='inputfile', type=str,
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
    from amami.um_utils.validation_tools import validate
    from amami.um_utils import read_fieldsfile
    from amami.quieterrors import QParseError

    inputFilename = args.inputfile
    fix = args.fix
    inplace = args.inplace
    others=args.others
    outFilename = args.outputfile

    if inputFilename is None:
        if others is not None:
            if len(others)==1:
                inputFilename = others[0]
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
            
    main(inputFilename,fix,inplace,outFilename)
