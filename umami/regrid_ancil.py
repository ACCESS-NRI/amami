#!/usr/bin/env python

# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

# Script screated by Davide Marchegiani ar ACCESS-NRI - davide.marchegiani@anu.edu.au

# Interpolate an ancillary file onto another grid

def read_files(inputFilename,gridFilename):
    # READ FILES
    inputFile = read_ancil(inputFilename)
    try:
        gridFile = read_ancil(gridFilename)
        umgrid=True
    except QValueError:
        try:
            gridFile = read_netCDF(gridFilename)
            umgrid=False
        except ValueError:
            raise QValueError(f"GRIDFILE must be either a UM ancillary file or a netCDF file.")
    print(f"====== Reading ancillary files OK! ======")
    return inputFile,gridFile,umgrid

def consistency_check(inputFile,gridFile,inputFilename,gridFilename,umgrid,latcoord=None,loncoord=None,levcoord=None,pseudocoord=None,fix=False):
    print("====== Consistency check... ======")
    # Check that both ancillary file and grid file are valid.
    # AncilFile
    inputFile = validate(inputFile,filename=inputFilename,fix=fix)
    nlat_input = len(get_latitude(inputFile))
    nlon_input = len(get_longitude(inputFile))
    lev_input_each_var,pseudo_input_each_var,_ = get_levels_each_var(inputFile)
    has_pseudo_each_var = has_pseudo_levels_each_var(inputFile)
    nvar_in = len(lev_input_each_var)

    # GridFile
    if umgrid: #If the grid is a um ancil file
        gridFile = validate(gridFile,filename=gridFilename,fix=fix)
        lat_out = get_latitude(gridFile)
        lon_out = get_longitude(gridFile)
        nlat_out = len(lat_out)
        nlon_out = len(lon_out)
        lev_out_each_var,pseudo_out_each_var,_ = get_levels_each_var(gridFile)
        nvar_out = len(lev_out_each_var)
        # Check consistency with number of data variables
        if (nvar_out < nvar_in) and (nvar_out == 1):
            lev_out_each_var = np.repeat(lev_out_each_var,nvar_in,axis=0).tolist()
            pseudo_out_each_var = np.repeat(pseudo_out_each_var,nvar_in,axis=0).tolist()
        elif nvar_out != nvar_in:
            raise QValueError(f"Number of data variables inconsistent. The input file '{inputFilename}' has {nvar_in} data variables, "
                f"the grid file '{gridFilename}' has {nvar_out} data variables.")
    else: #If the grid is a netCDF file
        nvar_out = len(gridFile.data_vars)
        # Check consistency with number of data variables
        if (nvar_out > nvar_in) or ((nvar_out < nvar_in) and (nvar_out != 1)):
            raise QValueError(f"Number of data variables inconsistent. The input file '{inputFilename}' has {nvar_in} data variables, "
                f"the grid file '{gridFilename}' has {nvar_out} data variables.")
        # Check latitude
        lat_out = check_latitude(gridFile,latcoord=latcoord)[0]
        nlat_out = len(lat_out)
        # Check longitude
        lon_out = check_longitude(gridFile,loncoord=loncoord)[0]
        nlon_out = len(lon_out)
        # Check level
        lev_out_each_var = check_levels(gridFile,has_pseudo_each_var,lev_input_each_var,levcoord=levcoord)[0]
        # Check pseudo-level
        pseudo_out_each_var = check_pseudo(gridFile,has_pseudo_each_var,pseudo_input_each_var,pseudocoord=pseudocoord)[0]

    # Check that both InputFile and gridFile are consistent in case latitude, longitude or levels are of length 1
    # Check Latitude
    if (nlat_input == 1 and nlat_out != 1):
        raise QValueError(f"Latitude is inconsistent! Ancillary file '{inputFilename}' has no latitude dimension "
                f"but the grid file '{gridFilename}' has a latitude length of {nlat_out}.")
    elif (nlat_input != 1 and nlat_out == 1):
        raise QValueError(f"Latitude is inconsistent! Grid file '{gridFilename}' has no latitude dimension "
                f"but the ancillary file '{inputFilename}' has a latitude length of {nlat_input}.")
    # Check Longitude
    if (nlon_input == 1 and nlon_out != 1):
        raise QValueError(f"Longitude is inconsistent! Ancillary file '{inputFilename}' has no longitude dimension "
                f"but the grid file '{gridFilename}' has a longitude length of {nlon_out}.")
    elif (nlon_input != 1 and nlon_out == 1):
        raise QValueError(f"Longitude is inconsistent! Grid file '{gridFilename}' has no longitude dimension "
                f"but the ancillary file '{inputFilename}' has a longitude length of {nlon_input}.")
    # Check Level
    for olev,ilev,ilvl in zip(lev_out_each_var,lev_input_each_var,range(len(lev_out_each_var))):
        if (len(ilev) == 1) and (len(olev) != 1):
            raise QValueError(f"Levels are inconsistent! Variable {ilvl+1} of the ancillary file '{inputFilename}' has no vertical level dimension "
                    f"but variable {ilvl+1} of the grid file '{gridFilename}' has {len(olev)} vertical levels.")
        elif (len(ilev) != 1) and (len(olev) == 1):
            raise QValueError(f"Levels are inconsistent! Variable {ilvl+1} of the grid file '{gridFilename}' has no vertical level dimension "
                    f"but variable {ilvl+1} of the ancillary file '{inputFilename}' has {len(ilev)} vertical levels.")
    
    # Repeat first variable grid in case grid file has only 1 variable and input file has more
        if nvar_out < nvar_in:
            lev_out_each_var = np.repeat(lev_out_each_var,nvar_in,axis=0).tolist()
            pseudo_out_each_var = np.repeat(pseudo_out_each_var,nvar_in,axis=0).tolist()

    # Change lev out in case of pseudo-levels
    levels_out = [pseudo_out_each_var[ivar] if ps else lev_out_each_var[ivar] for ivar,ps in enumerate(has_pseudo_each_var)]

    print("====== Consistency check OK! ======")
    return lat_out,lon_out,levels_out,inputFile

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
    outputFile = regrid_ancil(inputFile,lat_out,lon_out,lev_out,method)
    outputFile.to_file(outputFilename)
    print(f"====== Regridding and writing '{outputFilename}' OK! ======")

def main(inputFilename,gridFilename,outputFilename,loncoord,latcoord,levcoord,pseudocoord,method,fix):
    inputFile,gridFile,umgrid = read_files(inputFilename,gridFilename)
    lat_out,lon_out,lev_out,inputFile = consistency_check(inputFile,gridFile,inputFilename,gridFilename,umgrid,latcoord,loncoord,levcoord,pseudocoord,fix)
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
                        help='If GRIDFILE is a netCDF file, name of the latitude dimension in it.')
    parser.add_argument('--lon', '--longitude', dest='ncfile_longitude_name', required=False, type=str,
                        help='If GRIDFILE is a netCDF file, name of the longitude dimension in it.')
    parser.add_argument('--lev', '--level', dest='ncfile_level_name', required=False, type=str,
                        help='If GRIDFILE is a netCDF file, name of the vertical level dimension in it.')
    parser.add_argument('--ps', '--pseudo', dest='pseudo_level_name', required=False, type=str,
                    help='If GRIDFILE is a netCDF file, name of the pseudo-level dimension in the netCDF file.')
    parser.add_argument('--method', dest='method', required=False, type=str,
                    help="Choose the interpolation method among ('linear', 'nearest', 'cubic', 'quintic', 'pchip').")
    parser.add_argument('--fix', dest='fix', action='store_true', 
                        help="Try to fix any validation error.")

    args = parser.parse_args()

    # Imports here to improve performance when running with '--help' option
    import warnings
    import numpy as np
    warnings.filterwarnings("ignore")
    from umami.ancil_utils import regrid_ancil,read_ancil,get_levels_each_var,has_pseudo_levels_each_var,get_latitude,get_longitude
    from umami.netcdf_utils import read_netCDF,check_latitude,check_longitude,check_levels,check_pseudo
    from umami.ancil_utils.validation_tools import validate
    from umami.quieterrors import QValueError
    import os

    inputFilename=os.path.abspath(args.um_input_file)
    gridFilename=os.path.abspath(args.gridfile)
    outputFilename=args.um_output_file
    latcoord=args.ncfile_latitude_name
    loncoord=args.ncfile_longitude_name
    levcoord=args.ncfile_level_name
    pseudocoord=args.pseudo_level_name
    method=args.method 
    fix=args.fix

    print(f"====== Reading ancillary files... ======")

    main(inputFilename,gridFilename,outputFilename,loncoord,latcoord,levcoord,pseudocoord,method,fix)