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
def consistency_check(inputFile,ncFile,inputFilename,latcoord=None,loncoord=None,levcoord=None,pseudocoord=None,tcoord=None,fix=False):
    print("====== Consistency check... ======")
    # Check that ancillary file is valid.
    inputFile = validate(inputFile,filename=inputFilename,fix=fix)
    input_levels, input_pseudo_levels, _ = get_levels_each_var(inputFile)
    has_pseudo = has_pseudo_levels_each_var(inputFile)
    
    # Check that the number of variables is consistent
    nvarnc = len(ncFile.data_vars)
    nvarancil = len(input_levels)
    if nvarnc != nvarancil:
        raise QValueError(f"Number of data variables not consistent!\n"
                f"Number of data variables in the ancillary file: {nvarancil}. "
                f"Number of data variables in the netCDF file: {nvarnc}.")
    
    # Check that longitude, latitude and time coords are present in the .nc file and they have consistent lenghts with the ancillary file
    # Check latitude
    lat_out,latcoord = check_latitude(ncFile,latcoord=latcoord)
    nlat_out=len(lat_out)
    # Check that latitude dimension is consistent
    if (not regrid) and (nlat_out != inputFile.integer_constants.num_rows):
        raise QValueError(f"Latitude dimension not consistent!\nLength of netCDF file's latitude: {nlat_out}."
            f" Length of ancillary file's latitude: {inputFile.integer_constants.num_rows}."
            "\nIf you want to regrid the ancillary file onto the netCDF grid, please use the '--regrid' option.")

    # Check longitude
    lon_out,loncoord = check_longitude(ncFile,loncoord=loncoord)
    nlon_out=len(lon_out)
    # Check that longitude dimension is consistent
    if (not regrid) and (nlon_out != inputFile.integer_constants.num_cols):
        raise QValueError(f"Longitude dimension not consistent!\nLength of netCDF file's longitude: {nlon_out}."
            f" Length of ancillary file's longitude: {inputFile.integer_constants.num_cols}."
            "\nIf you want to regrid the ancillary file onto the netCDF grid, please use the '--regrid' option.")

    # Check time
    t_out,tcoord = check_time(ncFile,tcoord=tcoord)
    ntime=len(t_out)
    # Check that time dimension is consistent
    if ntime != inputFile.integer_constants.num_times:
        raise QValueError(f"Time dimension not consistent!\nLength of netCDF file's time: {ntime}."
            f" Length of ancillary file's time: {inputFile.integer_constants.num_times}.")
    
    # Check levels
    lev_out_each_var,levcoord = check_level(inputFile,has_pseudo,input_levels,levcoord=levcoord)
    # Check that level dimension is consistent
    if not regrid:
        for i,l in enumerate(lev_out_each_var):
            if len(l) != len(input_levels[i]):
                raise QValueError(f"Level dimension not consistent for variable {i+1}!\nNumber of levels in netCDF file: {len(l)}."
                    f" Number of levels in ancillary file: {len(input_levels[i])}."
                    "\nIf you want to regrid the ancillary file onto the netCDF grid, please use the '--regrid' option.")

    # Check Pseudo-levels
    pseudo_out_each_var,pseudocoord = check_pseudo(inputFile,has_pseudo,input_pseudo_levels,pseudocoord=pseudocoord)
    # Check that pseudo-levels are consistent
    if not regrid:
        for i,ps in enumerate(pseudo_out_each_var):
            if len(ps) != len(input_pseudo_levels[i]):
                raise QValueError(f"Psuedo-level dimension not consistent for variable {i+1}!\nNumber of pseudo-levels in netCDF file: {len(ps)}."
                    f" Number of pseudo-levels in ancillary file: {len(input_pseudo_levels[i])}."
                    "\nIf you want to regrid the ancillary file onto the netCDF grid, please use the '--regrid' option.")

    levels_out = [pseudo_out_each_var[ivar] if ps else lev_out_each_var[ivar] for ivar,ps in enumerate(has_pseudo)]
    levelcoord = [levcoord,pseudocoord]
    
    # Check that NC File doesn't have any additional variables
    dims=[tcoord,latcoord,loncoord]
    for var,ps in zip(ncFile.data_vars,has_pseudo):
        for d in ncFile[var].dims:
            if d not in (dims+[levelcoord[int(ps)]]) and len(ncFile[var][d])>1:
                raise QValueError(f"There is an extra dimension '{d}' in the netCDF variable '{var}'.")

    print("====== Consistency check OK! ======")
    return lat_out, latcoord, lon_out, loncoord, levels_out, levelcoord, ntime, tcoord, inputFile

def modify_and_write(inputFile,inputFilename,outputFilename,ncFile,regrid,lat_out,latcoord,lon_out,loncoord,lev_out,levcoord,ntime,tcoord,nanval):
    # WRITE FILE
    if outputFilename is None:
        outputFilename=inputFilename+"_modified"
        k=0
        while os.path.isfile(outputFilename):
            k+=1
            outputFilename = outputFilename+str(k)
    else:
        outputFilename = os.path.abspath(outputFilename)
    
    def substitute_nanval(data):
        if nanval is None:
            return data.where(data.notnull(),UM_NANVAL).transpose(latcoord,loncoord).values
        else:
            return data.where(data != nanval, UM_NANVAL).transpose(latcoord,loncoord).values

    def select_time_level(data,tind=None,lvind=None):
        if tcoord is not None:
            data = data.isel({tcoord:tind}, drop=True)
        if levcoord is not None:
            data = data.isel({levcoord:lvind}, drop=True)
        return data

    def get_2d_data(data,tind,lvind):
        return substitute_nanval(select_time_level(data,tind,lvind)).squeeze()

    if regrid:
        print(f"====== Regridding '{outputFilename}'... ======")
        newAncilFile = regrid_ancil(inputFile,lat_out,lon_out,lev_out)
        print(f"====== Regridding '{outputFilename}' OK! ======")
    else:
        # Create a copy of the ancillary file to modify
        newAncilFile = inputFile.copy(include_fields=True)

    print(f"====== Modifying and writing '{outputFilename}'... ======")

    fldind = iter(newAncilFile.fields)
    for t in range(ntime):
        f=next(fldind)
        for var in ncFile.data_vars:
            for lv,_ in enumerate(lev_out):
                data_2d = get_2d_data(ncFile[var],t,lv)
                f.set_data_provider(mule.ArrayDataProvider(data_2d))

    newAncilFile.to_file(outputFilename)
    print(f"====== Writing '{outputFilename}' ancillary file OK! ======")

def main(inputFilename,ncFilename,outputFilename,latcoord,loncoord,tcoord,levcoord,pseudocoord,nanval,regrid,fix):
        inputFile,ncFile = read_files(inputFilename,ncFilename)
        lat_out, latcoord, lon_out, loncoord, levels_out, levelcoord, ntime, tcoord, inputFile = consistency_check(inputFile,ncFile,inputFilename,latcoord,loncoord,levcoord,pseudocoord,tcoord,fix)
        modify_and_write(inputFile,inputFilename,outputFilename,ncFile,regrid,lat_out,latcoord,lon_out,loncoord,levels_out,levelcoord,ntime,tcoord,nanval)

if __name__ == '__main__':
    import argparse

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

    # Imports here to improve performance when running with '--help' option
    import os
    import mule
    import xarray as xr
    from umami.ancil_utils.validation_tools import validate
    import warnings
    warnings.filterwarnings("ignore")
    from umami.ancil_utils import UM_NANVAL, read_ancil, get_levels_each_var, has_pseudo_levels_each_var, regrid_ancil
    from umami.netcdf_utils import check_latitude, check_longitude, check_level, check_pseudo, check_time
    from umami.quieterrors import QValueError

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

    (inputFilename,ncFilename,outputFilename,latcoord,loncoord,tcoord,
        levcoord,pseudocoord,nanval,regrid,fix) = (
        "/g/data/w40/dxd565/um-reosc-slab/ancil/vavqa.reosc.ancil",
        "/g/data/w40/sza565/ancil_data/vavqa.reosc.ancil.shiftANZ.nc",
        "/g/data3/tm70/dm5220/ancil/abhik/shifted/vavqa.reosc.ancil.shiftANZ",
        None,
        None,
        None,
        None,
        None,
        None,
        False,
        True,
        )
    print(f"====== Reading '{inputFilename}' ancillary file... ======")

    main(inputFilename,ncFilename,outputFilename,latcoord,loncoord,tcoord,
        levcoord,pseudocoord,nanval,regrid,fix)




