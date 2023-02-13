#!/usr/bin/env python

# Script created by Davide Marchegiani (davide.marchegiani@anu.edu.au) at ACCESS-NRI.

# Validate a UM ancillary file

def main(ancilFilename,fix,inplace):
    ancilFilename = os.path.abspath(ancilFilename)
    ancilFile = read_ancil(ancilFilename)
    outFile = validate(ancilFile,fix=fix)
    if outFile is not None:
        if inplace:
            outFilename = ancilFilename
        else:
            outFilename = ancilFilename + '_fixed'
        outFile.to_file(outFilename)
        print(f"Fixing completed! Written '{outFilename}' to disk.")
    else:
        print(f"'{ancilFilename}' is a valid ancillary file!")

if __name__ == '__main__':
    import argparse
    import sys
    # Parse arguments
    parser = argparse.ArgumentParser(description="Validate UM ancillary file.",allow_abbrev=False)
    parser.add_argument('-i', '--input', dest='ancilfile', type=str,
                        help='UM ancillary input file.')
    parser.add_argument('--fix', dest='fix', action='store_true', 
        help="Try to fix any validation error and write a new file with '_fixed' appended."+\
            "Use the '--inplace' option to modify the input file in place.")
    parser.add_argument('--inplace', dest='inplace', action='store_true', 
        help='Change the file in place, instead of creating a new one.')
    parser.add_argument('others', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    ancilFilename = args.ancilfile
    fix = args.fix
    inplace = args.inplace
    others=args.others

    if ancilFilename is None:
        if others is not None:
            if len(others)==1:
                ancilFilename = others[0]
            elif len(others)>1:
                if '--fix' in others or '--inplace' in others:
                    sys.exit("Please place any option before input ancillary file.")
                else:    
                    sys.exit("Too many arguments.")
        else:
            sys.exit("The input ancillary file is required.")
            

    # Imports here to improve performance when running with '--help' option
    import warnings
    import os
    warnings.filterwarnings("ignore")
    from umami.utils.validation_tools import validate
    from umami.utils import read_ancil

    main(ancilFilename,fix,inplace)
