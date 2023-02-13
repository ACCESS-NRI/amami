#!/usr/bin/env python

# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

# Script screated by Davide Marchegiani ar ACCESS-NRI - davide.marchegiani@anu.edu.au

# Interpolate an ancillary file onto another grid

def read_files(inputFilename,gridFilename):
    print(f"====== Reading '{inputFilename}' ancillary file... ======", end="\r")
    # READ FILES
    inputFile = read_ancil(inputFilename)
    try:
        gridFile = read_ancil(gridFilename)
        umgrid=True
    except ValueError:
        try:
            gridFile = xr.load_dataset(gridFilename)
            umgrid=False
        except ValueError:
            sys.exit(f"GRIDFILE must be either a UM ancillary file or a netCDF file.")
    print(f"====== Reading '{inputFilename}' ancillary file OK! ======")
    return inputFile,gridFile,umgrid

def consistency_check(inputFile,gridFile,umgrid,latcoord=None,loncoord=None,levcoord=None):
    print("====== Consistency check... ======", end="\r")
    # Check that both ancillary file and grid file are valid.
    # AncilFile
    validate(inputFile)
    nlat_input = inputFile.integer_constants.num_rows
    nlon_input = inputFile.integer_constants.num_cols
    nlev_input = inputFile.integer_constants.num_levels
    
    # GridFile
    if umgrid: #If the grid is a um ancil file
        validate(gridFile)
        nlat_target = gridFile.integer_constants.num_rows
        firstlat_target = gridFile.real_constants.start_lat
        dlat_target = gridFile.real_constants.row_spacing
        nlon_target = gridFile.integer_constants.num_cols
        firstlon_target = gridFile.real_constants.start_lon
        dlon_target = gridFile.real_constants.col_spacing
        nlev_target = gridFile.integer_constants.num_levels
        lat_out = [firstlat_target+dlat_target*i for i in range(nlat_target)]
        lon_out = [firstlon_target+dlon_target*i for i in range(nlon_target)]
    else: #If the grid is a netCDF file
        # Check latitude
        if latcoord is None: #If user has not defined any latitude name
            latcoord = get_dim_name_from_netcdf(gridFile,
                dim_names=('latitude','lat'),
                errmsg="No latitude dimension found in the netCDF file.\n"+\
                        "To specify the name of the latitude dimension in the netCDF "+\
                        "file use the '--latitude <name>' option.")
        elif latcoord not in gridFile.dims:
            sys.exit(f"Specified latitude dimension '{latcoord}' not found in netCDF file.")
        nlat_target = len(gridFile[latcoord])
        lat_out = gridFile[latcoord].values
        # Check longitude
        if loncoord is None: #If user has not defined any longitude name
            loncoord = get_dim_name_from_netcdf(gridFile,
                dim_names=('longitude','lon'),
                errmsg="No longitude dimension found in the netCDF file.\n"+\
                        "To specify the name of the longitude dimension in the netCDF "+\
                        "file use the '--longitude <name>' option.")
        elif loncoord not in gridFile.dims:
            sys.exit(f"Specified longitude dimension '{loncoord}' not found in netCDF file.")
        nlon_target = len(gridFile[loncoord])
        lon_out = gridFile[loncoord].values
        # Check level
        if levcoord is None: #If user has not defined any level name
            levcoord = get_dim_name_from_netcdf(gridFile,
                dim_names=("hybrid","sigma","pressure","depth","surface","vertical_level"),
                errmsg="No vertical level dimension found in the netCDF file.\n"+\
                        "To specify the name of the vertical level dimension in the netCDF "+\
                        "file use the '--level <name>' option.")
        elif levcoord not in gridFile.dims:
            sys.exit(f"Specified vertical level dimension '{levcoord}' not found in netCDF file.")
        nlev_target = len(gridFile.dims[levcoord])

    # Check that both InputFile and gridFile are consistent in case latitude, longitude or levels are of length 1
    # Check Latitude
    if (nlat_input == 1 and nlat_target != 1):
        sys.exit(f"Latitude is inconsistent! Ancillary file '{inputFilename}' has no latitude dimension "+\
                f"but the grid file '{gridFilename}' has a latitude length of {nlat_target}.")
    elif (nlat_input != 1 and nlat_target == 1):
        sys.exit(f"Latitude is inconsistent! Grid file '{gridFilename}' has no latitude dimension "+\
                f"but the ancillary file '{inputFilename}' has a latitude length of {nlat_input}.")
    # Check Longitude
    if (nlon_input == 1 and nlon_target != 1):
        sys.exit(f"Longitude is inconsistent! Ancillary file '{inputFilename}' has no longitude dimension "+\
                f"but the grid file '{gridFilename}' has a longitude length of {nlon_target}.")
    elif (nlon_input != 1 and nlon_target == 1):
        sys.exit(f"Longitude is inconsistent! Grid file '{gridFilename}' has no longitude dimension "+\
                f"but the ancillary file '{inputFilename}' has a longitude length of {nlon_input}.")
    # Check Level
    if (nlev_input == 1 and nlev_target != 1):
        sys.exit(f"Levels are inconsistent! Ancillary file '{inputFilename}' has no vertical level dimension "+\
                f"but the grid file '{gridFilename}' has {nlev_target} vertical levels.")
    elif (nlev_input != 1 and nlev_target == 1):
        sys.exit(f"Levels are inconsistent! Grid file '{gridFilename}' has no vertical level dimension "+\
                f"but the ancillary file '{inputFilename}' has {nlev_input} vertical levels.")
    print("====== Consistency check OK! ======")
    return lat_out,lon_out,nlev_target

def regrid_and_write(inputFile,lat_out,lon_out,nlev_out,outputFilename):
    print(f"====== Regridding and writing '{outputFilename}' ancillary file... ======", end="\r")
    if outputFilename is None:
        outputFilename=inputFilename+"_regridded"
        k=0
        while os.path.isfile(outputFilename):
            k+=1
            outputFilename = outputFilename+str(k)
    else:
        outputFilename = os.path.abspath(outputFilename)

    outputFile = regrid_ancil(inputFile,lat_out,lon_out,nlev_out)
    outputFile.to_file(outputFilename)
    print(f"====== Regridding and writing '{outputFilename}' ancillary file OK! ======")

def main(inputFilename,gridFilename,outputFilename,loncoord,latcoord,levcoord):
    inputFile,gridFile,umgrid = read_files(inputFilename,gridFilename)
    lat_out,lon_out,nlev_out = consistency_check(inputFile,gridFile,umgrid,latcoord,loncoord,levcoord)
    regrid_and_write(inputFile,lat_out,lon_out,nlev_out,outputFilename)

if __name__ == '__main__':

    import argparse
    import os

    # Parse arguments
    description='''Regrid UM ancillary file onto another ancillary file or netCDF file grid.'''
    parser = argparse.ArgumentParser(description=description, allow_abbrev=False)
    parser.add_argument('-i', '--input', dest='um_input_file', required=True, type=str,
                        help='UM ancillary input file. (Required)')
    parser.add_argument('-g', "--grid", dest='gridfile', required=True, type=str,
                        help='UM ancillary file or netCDF file on the new grid. (Required)')
    parser.add_argument('-o', '--output', dest='um_output_file', required=False, type=str,
                        help='UM ancillary output file.')
    parser.add_argument('--lat', '--latitude', dest='ncfile_latitude_name', required=False, type=str,
                        help='Name of the latitude dimension in the netCDF file.')
    parser.add_argument('--lon', '--longitude', dest='ncfile_longitude_name', required=False, type=str,
                        help='Name of the longitude dimension in the netCDF file.')
    parser.add_argument('--lev', '--level', dest='ncfile_level_name', required=False, type=str,
                        help='Name of the level dimension in the netCDF file.')

    args = parser.parse_args()
    inputFilename=os.path.abspath(args.um_input_file)
    gridFilename=os.path.abspath(args.gridfile)
    outputFilename=args.um_output_file
    latcoord=args.ncfile_latitude_name
    loncoord=args.ncfile_longitude_name
    levcoord=args.ncfile_level_name

    # Imports here to improve performance when running with '--help' option
    import sys
    import mule
    import xarray as xr
    import warnings
    warnings.filterwarnings("ignore")
    from umami.utils import regrid_ancil, get_dim_name_from_netcdf, read_ancil
    from umami.utils.validation_tools import validate


    main(inputFilename,gridFilename,outputFilename,loncoord,latcoord,levcoord)