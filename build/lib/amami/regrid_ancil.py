#!/usr/bin/env python3

# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

# Script created by Davide Marchegiani ar ACCESS-NRI - davide.marchegiani@anu.edu.au

# Interpolate an ancillary file onto another grid

def read_files(inputFilename,gridFilename):
    # READ FILES
    inputFile = read_fieldsfile(inputFilename)
    try:
        gridFile = read_fieldsfile(gridFilename)
        umgrid=True
    except QValueError:
        try:
            gridFile = read_netCDF(gridFilename)
            umgrid=False
        except ValueError:
            raise QValueError(f"GRIDFILE must be either a UM ancillary file or a netCDF file.")
    print(f"====== Reading files OK! ======")
    return inputFile,gridFile,umgrid

def consistency_check(inputFile,gridFile,inputFilename,gridFilename,umgrid,latcoord=None,loncoord=None,levcoord=None,fix=False):
    print("====== Consistency check... ======")
    # Check that both ancillary file and grid file are valid.
    # AncilFile
    inputFile = validate(inputFile,filename=inputFilename,fix=fix)
    nlat_in_each_var = [len(l) for l in get_latitude_each_var(inputFile)]
    nlon_in_each_var = [len(l) for l in get_longitude_each_var(inputFile)]
    lev_in_each_var,pseudo_in_each_var = get_levels_each_var(inputFile)
    has_pseudo_in_each_var = has_pseudo_each_var(inputFile)
    levels_in_each_var = [pseudo_in_each_var[ivar] if ps else lev_in_each_var[ivar] for ivar,ps in enumerate(has_pseudo_in_each_var)]
    nvar_in = len(lev_in_each_var)

    # GridFile
    if umgrid: #If the grid is a um ancil file
        gridFile = validate(gridFile,filename=gridFilename,fix=fix)
        lat_out_each_var = get_latitude_each_var(gridFile)
        lon_out_each_var = get_longitude_each_var(gridFile)
        nlat_out_each_var = [len(l) for l in lat_out_each_var]
        nlon_out_each_var = [len(l) for l in lon_out_each_var]
        lev_out_each_var,pseudo_out_each_var = get_levels_each_var(gridFile)
        nvar_out = len(lev_out_each_var)
        # Check consistency with number of data variables
        if (nvar_out < nvar_in) and (nvar_out == 1):
            lat_out_each_var = np.repeat(lat_out_each_var,nvar_in,axis=0).tolist()
            lon_out_each_var = np.repeat(lon_out_each_var,nvar_in,axis=0).tolist()
            lev_out_each_var = np.repeat(lev_out_each_var,nvar_in,axis=0).tolist()
            pseudo_out_each_var = np.repeat(pseudo_out_each_var,nvar_in,axis=0).tolist()
        elif nvar_out != nvar_in:
            raise QValueError(f"Number of data variables inconsistent. The input file '{inputFilename}' has {nvar_in} data variables, "
                f"the grid file '{gridFilename}' has {nvar_out} data variables.")
        # Change lev out in case of pseudo-levels
        levels_out_each_var = [pseudo_out_each_var[ivar] if ps else lev_out_each_var[ivar] for ivar,ps in enumerate(has_pseudo_in_each_var)]
    else: #If the grid is a netCDF file
        nvar_out = len(gridFile.data_vars)
        # Check consistency with number of data variables
        if (nvar_out > nvar_in) or ((nvar_out < nvar_in) and (nvar_out != 1)):
            raise QValueError(f"Number of data variables inconsistent. The input file '{inputFilename}' has {nvar_in} data variables, "
                f"the grid file '{gridFilename}' has {nvar_out} data variables.")
        # Check latitude
        lat_out_each_var = check_latitude(gridFile,latcoord=latcoord)[0]
        nlat_out_each_var = [len(l) for l in lat_out_each_var]
        # Check longitude
        lon_out_each_var = check_longitude(gridFile,loncoord=loncoord)[0]
        nlon_out_each_var = [len(l) for l in lon_out_each_var]
        # Check level
        levels_out_each_var = check_level(gridFile,levcoord=levcoord)[0]
        # Check consistency with number of data variables
        if (nvar_out < nvar_in):
            lat_out_each_var = np.repeat(lat_out_each_var,nvar_in,axis=0).tolist()
            lon_out_each_var = np.repeat(lon_out_each_var,nvar_in,axis=0).tolist()
            levels_out_each_var = np.repeat(levels_out_each_var,nvar_in,axis=0).tolist()
    
    print("====== Consistency check OK! ======")
    return lat_out_each_var,lon_out_each_var,levels_out_each_var,inputFile

def regrid_and_write(inputFile,inputFilename,lat_out,lon_out,lev_out,method,outputFilename):
    if outputFilename is None:
        outputFilename=inputFilename+"_regridded"
        k=0
        while os.path.isfile(outputFilename):
            k+=1
            outputFilename = outputFilename+str(k)
    else:
        outputFilename = os.path.abspath(outputFilename)
    print(f"====== Regridding and writing '{outputFilename}'... ======")
    # Create directories
    os.makedirs(os.path.dirname(outputFilename),exist_ok=True)
    outputFile = regrid_fieldsfile(inputFile,lat_out,lon_out,lev_out,method)
    outputFile.to_file(outputFilename)
    print(f"====== Regridding and writing '{outputFilename}' OK! ======")

def main(inputFilename,gridFilename,outputFilename,loncoord,latcoord,levcoord,method,fix):
    inputFile,gridFile,umgrid = read_files(inputFilename,gridFilename)
    lat_out,lon_out,lev_out,inputFile = consistency_check(inputFile,gridFile,inputFilename,gridFilename,umgrid,latcoord,loncoord,levcoord,fix)
    regrid_and_write(inputFile,inputFilename,lat_out,lon_out,lev_out,method,outputFilename)

if __name__ == '__main__':
    import argparse

    # Parse arguments
    description='''Regrid UM ancillary file onto another ancillary file or netCDF file grid.
                   If using a netCDF file grid, any different number of vertical levels (including pseudo-levels) will be regridded based on 
                   a linear interpolation of the input vertical levels. This might generate different vertical levels values than those of 
                   the input file.
                '''
    parser = argparse.ArgumentParser(description=description, allow_abbrev=False)
    parser.add_argument('-i', '--input', dest='um_input_file', required=True, type=str,
                        help='UM ancillary input file. (Required)')
    parser.add_argument('-g', "--grid", dest='gridfile', required=True, type=str,
                        help='UM ancillary file or netCDF file on the new grid. (Required)')
    parser.add_argument('-o', '--output', dest='um_output_file', required=False, type=str,
                        help='UM ancillary output file.')
    parser.add_argument('--lat', '--latitude', dest='ncfile_latitude_name', required=False, type=str,
                        help="If GRIDFILE is a netCDF file, name of the netCDF variables' latitude dimension. "
                            "If the netCDF has different latitude names for different variables, list of the "
                            "latitude dimension names for every netCDF variable.")
    parser.add_argument('--lon', '--longitude', dest='ncfile_longitude_name', required=False, type=str,
                        help="If GRIDFILE is a netCDF file, name of the netCDF variables' longitude dimension. "
                            "If the netCDF has different longitude names for different variables, list of the "
                            "longitude dimension names for every netCDF variable.")
    parser.add_argument('--lev', '--level', dest='ncfile_level_name', required=False, type=str,
                        help="If GRIDFILE is a netCDF file, name of the netCDF variables' vertical level (or pseudo-level) dimension. "
                            "If the netCDF has different level names for different variables, list of the level "
                            "dimension names for every netCDF variable. If a variable does not have any vertical "
                            "dimension, use 'None' as a level name for that variable.")
    parser.add_argument('--method', dest='method', required=False, type=str,
                    help="Interpolation method to be chosen among ('linear', 'nearest', 'cubic', 'quintic', 'pchip'). "
                         "Default value 'nearest'.")
    parser.add_argument('--fix', dest='fix', action='store_true', 
                        help="Try to fix any ancillary validation error.")

    args = parser.parse_args()

    # Imports here to improve performance when running with '--help' option
    import warnings
    warnings.filterwarnings("ignore")
    import numpy as np
    from amami.um_utils import (UM_NANVAL, read_fieldsfile,get_latitude_each_var,get_longitude_each_var,
                                   get_levels_each_var,has_pseudo_each_var,regrid_fieldsfile)
    from amami.netcdf_utils import (split_coord_names,read_netCDF,check_latitude, check_longitude,
                                    check_level)
    from amami.um_utils.validation_tools import validate
    from amami.quieterrors import QValueError
    import os

    inputFilename=os.path.abspath(args.um_input_file)
    gridFilename=os.path.abspath(args.gridfile)
    outputFilename=args.um_output_file
    latcoord=split_coord_names(args.ncfile_latitude_name)
    loncoord=split_coord_names(args.ncfile_longitude_name)
    levcoord=split_coord_names(args.ncfile_level_name)
    method=args.method
    fix=args.fix
    
    print(f"====== Reading files... ======")

    main(inputFilename,gridFilename,outputFilename,loncoord,latcoord,levcoord,method,fix)