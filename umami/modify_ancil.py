#!/usr/bin/env python

# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

# Script created by Davide Marchegiani (davide.marchegiani@anu.edu.au) at ACCESS-NRI.

# Modify a UM ancillary file using data from a netCDF file


# READ FILES
def read_files(inputFilename,ncFilename):        
    inputFile = read_ancil(inputFilename)
    ncFile = xr.load_dataset(ncFilename, decode_times=False)
    print(f"====== Reading '{inputFilename}' ancillary file OK! ======")
    return inputFile, ncFile

# CONSISTENCY CHECK
def consistency_check(inputFile,ncFile,inputFilename,gridFilename,latcoord=None,loncoord=None,levcoord=None,fix=False):
    print("====== Consistency check... ======")
    # Check that ancillary file is valid.
    inputFile = validate(inputFile,filename=inputFilename,fix=fix)
    # Check that longitude, latitude and time coords are present in the .nc file and they have consistent lenghts with the ancillary file
    dims=list(ncFile.dims)
    
    # Check latitude
    if latcoord is None: #If user has not defined any latitude name
        latcoord = get_dim_name(ncFile,dim_names=('latitude','lat'),
            errmsg="No latitude dimension found in the netCDF file.\n"
                    "To specify the name of the latitude dimension in the netCDF "
                    "file use the '--latitude <name>' option.")
    elif latcoord not in dims:
        raise QValueError(f"Specified latitude dimension '{latcoord}' not found in netCDF file.")
    lat_out = ncFile[latcoord].values
    nlat_out=len(lat_out)
    # Check that latitude dimension is consistent
    if (not regrid) and (nlat_out != inputFile.integer_constants.num_rows):
        raise QValueError(f"Latitude dimension not consistent!\nLength of netCDF file's latitude: {nlat_out}."
            f" Length of ancillary file's latitude: {inputFile.integer_constants.num_rows}."
            "\nIf you want to regrid the ancillary file onto the netCDF grid, please use the '--regrid' option.")
    dims.remove(latcoord)

    # Check longitude
    if loncoord is None: #If user has not defined any longitude name
        loncoord = get_dim_name(ncFile,dim_names=('longitude','lon'),
            errmsg="No longitude dimension found in the netCDF file.\n"
                    "To specify the name of the longitude dimension in the netCDF "
                    "file use the '--longitude <name>' option.")
    elif loncoord not in dims:
        raise QValueError(f"Specified longitude dimension '{loncoord}' not found in netCDF file.")
    lon_out = ncFile[loncoord].values
    nlon_out=len(lon_out)
    # Check that longitude dimension is consistent
    if (not regrid) and (nlon_out != inputFile.integer_constants.num_cols):
        raise QValueError(f"Longitude dimension not consistent!\nLength of netCDF file's longitude: {nlon_out}."
            f" Length of ancillary file's longitude: {inputFile.integer_constants.num_cols}."
            "\nIf you want to regrid the ancillary file onto the netCDF grid, please use the '--regrid' option.")
    dims.remove(loncoord)

    # Check time
    if inputFile.integer_constants.num_times > 1:
        if tcoord is None: #If user has not defined any longitude name
            tcoord = get_dim_name(ncFile,dim_names=('time','t'),
                errmsg="No time dimension found in the netCDF file.\n"
                        "To specify the name of the time dimension in the netCDF "
                        "file use the '--time <name>' option.")
        elif tcoord not in dims:
            raise QValueError(f"Specified longitude dimension '{tcoord}' not found in netCDF file.")
        ntime=len(ncFile[tcoord])
        dims.remove(tcoord)
    else:
        ntime = 1
    # Check that time dimension is consistent
    if ntime != inputFile.integer_constants.num_times:
        raise QValueError(f"Time dimension not consistent!\nLength of netCDF file's time: {ntime}."
            f" Length of ancillary file's time: {inputFile.integer_constants.num_times}.")
    
    # Check level
    nlev_input = len(get_levels_each_var(inputFile)[0])
    if levcoord is None:
        if nlev_input == 1:
            lev_out, nlev_out = 1, 1
        elif len(dims) > 0:
            levcoord = get_dim_name(ncFile,dim_names=("hybrid","sigma","pressure","depth","surface","vertical_level"),
                errmsg="No level dimension found in the netCDF file.\n"
                        "To specify the name of the level dimension in the netCDF "
                        "file use the '--level <name>' option.")
            lev_out = ncFile[levcoord].values
            nlev_out=len(lev_out)
            dims.remove(levcoord)
        else:
            raise QValueError(f"Vertical levels found in the ancillary file, but no vertical level dimension found in the netCDF file.")
    elif levcoord not in ncFile.dims:
        raise QValueError(f"Specified level dimension '{levcoord}' not found in netCDF file.")
    else:
        lev_out = ncFile[levcoord].values
        nlev_out=len(lev_out)
        dims.remove(levcoord)
    # Check that level dimension is consistent
    if (not regrid) and (nlev_out != nlev_input):
        raise QValueError(f"Level dimension not consistent!\nLength of netCDF file's level: {nlev_out}."
            f" Length of ancillary file's level: {inputFile.integer_constants.num_cols}."
            "\nIf you want to regrid the ancillary file onto the netCDF grid, please use the '--regrid' option.")

    # Pseudo-levels
    if sum([f.lbuser5 for f in inputFile.fields]) != 0:
        if nlev_out != 1:
            raise QValueError(f"Pseudo-levels found in the ancillary file and number of levels in the netCDF > 1.")
        elif pseudocoord is None: #If user has not defined any pseudo-level name
            # Check if ancillary file has pseudo-levels
                if len(dims) > 0:
                    pseudocoord = get_dim_name(ncFile,dim_names=("pseudo"),
                    errmsg="Pseudo-levels found in the ancillary file, but no pseudo-level dimension found in the netCDF file.\n"
                            "To specify the name of the pseudo-level dimension in the netCDF "
                            "file use the '--pseudo <name>' option.")
                    npseudo = len(ncFile[pseudocoord])
                else:
                    raise QValueError(f"Pseudo-levels found in the ancillary file, but no pseudo-level dimension found in the netCDF file.")
        elif pseudocoord not in ncFile.dims:
            raise QValueError(f"Specified pseudo-level dimension '{pseudocoord}' not found in netCDF file.")
        else:
            npseudo = len(ncFile[pseudocoord])
        # Check that pseudo-levels are consistent
        pseudoLevs=[f.lbuser5 for f in inputFile.fields[:(len(inputFile.fields)//ntime)]]
        k=0
        for i,var in enumerate(ncFile.data_vars):
            if pseudocoord in ncFile[var].dims:
                if len(set(pseudoLevs[k:k+npseudo])) != npseudo:
                    raise QValueError(f"Pseudo dimension not consistent!\n"
                    f"Number of pseudo-levels in the ancillary variable n. {i}: {len(set(pseudoLevs[k:k+npseudo]))}."
                    f" Length of the '{pseudocoord}' dimension in the netCDF variable n. {i} ('{ncFile[var].name}'): {npseudo}.")
                k+=npseudo
            else:
                k+=1
    elif pseudocoord is not None:
        raise QValueError(f"Pseudo-level dimension '{pseudocoord}' specified, but no pseudo-level dimension found in the ancillary file.")
    
    # Check that the number of variables is consistent
    nvarsnc = len(ncFile.data_vars)
    nvarsancil = len(set([f.lbuser4 for f in inputFile.fields]))
    if nvarsnc != nvarsancil:
        raise QValueError(f"Number of data variables not consistent!\n"
                f"Number of data variables in the ancillary file: {nvarsancil}. "
                f"Number of data variables in the netCDF file: {nvarsnc}.")
    print("====== Consistency check OK! ======")
    return lat_out, lon_out, lev_out, pseudocoord, npseudo, ntime, dims, inputFile

def modify_and_write(inputFile,inputFilename,outputFilename,regrid,lat_out,lon_out,lev_out,pseudocoord,npseudo,ntime,dims,nanval):
    # WRITE FILE
    if outputFilename is None:
        outputFilename=inputFilename+"_modified"
        k=0
        while os.path.isfile(outputFilename):
            k+=1
            outputFilename = outputFilename+str(k)
    else:
        outputFilename = os.path.abspath(outputFilename)
    if regrid:
        regrid
    
    def substitute_nanval(data):
        if nanval is None:
            return data.where(data.notnull(),UM_NANVAL).transpose(latcoord,loncoord).values
        else:
            return data.where(data != nanval, UM_NANVAL).transpose(latcoord,loncoord).values

    def select_time_level(data,tind,lvind):
        if tcoord is not None:
            data = data.isel({tcoord:tind}, drop=True)
        if levcoord is not None:
            data = data.isel({levcoord:lvind}, drop=True)
        return data

    if regrid:
        print(f"====== Regridding '{outputFilename}'... ======")
        newAncilFile = regrid_ancil(inputFile,lat_out,lon_out,lev_out)
        print(f"====== Regridding '{outputFilename}' OK! ======")
    else:
        # Create a copy of the ancillary file to modify
        newAncilFile = inputFile.copy(include_fields=True)

    print(f"====== Modifying and writing '{outputFilename}'... ======")
    # Exclude extra dimensions
    if len(dims) > 0:
        ncFile=ncFile.drop(*dims)

    fldind = iter(newAncilFile.fields)
    for t in range(ntime):
        f=next(fldind)
        for var in ncFile.data_vars:
            for lv,_ in enumerate(lev_out):
                if pseudocoord in ncFile[var].dims:
                    for ps in range(npseudo):
                        data_2d = substitute_nanval(select_time_level(ncFile[var],t,lv).isel({pseudocoord:ps},drop=True))
                        f.set_data_provider(mule.ArrayDataProvider(data_2d))
                else:
                    data_2d = substitute_nanval(select_time_level(ncFile[var],t,lv))
                    f.set_data_provider(mule.ArrayDataProvider(data_2d))

    newAncilFile.to_file(outputFilename)
    print(f"====== Writing '{outputFilename}' ancillary file OK! ======")

def main(inputFilename,ncFilename,outputFilename,latcoord,loncoord,tcoord,levcoord,pseudocoord,nanval,regrid,fix):
        inputFile,ncFile = read_files(inputFilename,ncFilename)
        lat_out,lon_out,lev_out,pseudocoord,npseudo,ntime,dims,inputFile = consistency_check(inputFile,ncFile,inputFilename,ncFilename,latcoord,loncoord,levcoord,fix)
        modify_and_write(inputFile,inputFilename,outputFilename,regrid,lat_out,lon_out,lev_out,pseudocoord,npseudo,ntime,dims,nanval)

import argparse
import os

# Parse arguments
description = '''Modify a UM ancillary file using data from a netCDF file. If regridding is necessary, use the '--regrid' option.'''
parser = argparse.ArgumentParser(description=description, allow_abbrev=False)
parser.add_argument('-i', '--input', dest='um_input_file', required=True, type=str,
                    help='UM ancillary input file. (Required)')
parser.add_argument('--nc', '--ncfile', dest='ncfile', required=True, type=str,
                    help='NetCDF file to turn into UM ancillary file. (Required)')
parser.add_argument('-o', '--output', dest='um_output_file', required=False, type=str,
                    help='UM ancillary output file.')                    
parser.add_argument('--lat', '--latitude', dest='latitude_name', required=False, type=str,
                    help='Name of the latitude dimension in the netCDF file.')
parser.add_argument('--lon', '--longitude', dest='longitude_name', required=False, type=str,
                    help='Name of the longitude dimension in the netCDF file.')
parser.add_argument('-t', '--time', dest='time_name', required=False, type=str,
                    help='Name of the time dimension in the netCDF file.')
parser.add_argument('--lev', '--level', dest='level_name', required=False, type=str,
                    help='Name of the level dimension in the netCDF file.') 
parser.add_argument('--ps', '--pseudo', dest='pseudo_level_name', required=False, type=str,
                    help='Name of the pseudo-level dimension in the netCDF file.')
parser.add_argument('--nan', dest='nanval', required=False, type=float,
                    help='Value for NaNs in the netCDF file.')
parser.add_argument('--regrid', dest='regrid', action="store_true",
                    help='Regrid the input UM ancillary file onto the netCDF file grid.')
parser.add_argument('--fix', dest='fix', action='store_true', 
                    help="Try to fix any validation error.")

args = parser.parse_args()
inputFilename=os.path.abspath(args.um_input_file)
ncFilename=os.path.abspath(args.ncfile)
outputFilename=args.um_output_file
latcoord=args.latitude_name
loncoord=args.longitude_name
tcoord=args.time_name
levcoord=args.level_name
pseudocoord=args.pseudo_level_name
nanval=args.nanval
regrid=args.regrid
fix=args.fix

print(f"====== Reading '{inputFilename}' ancillary file... ======")

import mule
from mule.validators import ValidateError
import xarray as xr
import sys
import numpy as np
from umami.ancil_utils.validation_tools import validate
import warnings
warnings.filterwarnings("ignore")
from umami.ancil_utils import UM_NANVAL, read_ancil, get_levels_each_var, regrid_ancil
from umami.netcdf_utils import get_dim_name
from umami.quieterrors import QValueError

main(inputFilename,ncFilename,outputFilename,latcoord,loncoord,tcoord,
    levcoord,pseudocoord,nanval,regrid,fix)




