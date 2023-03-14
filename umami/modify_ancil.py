#!/usr/bin/env python

# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

# Script created by Davide Marchegiani (davide.marchegiani@anu.edu.au) at ACCESS-NRI.

# Modify a UM ancillary file using data from a netCDF file

# READ FILES
def read_files(inputFilename,ncFilename):        
    inputFile = read_ancil(inputFilename)
    ncFile = read_netCDF(ncFilename)
    print(f"====== Reading '{inputFilename}' ancillary file OK! ======")
    return inputFile, ncFile

# CONSISTENCY CHECK
def consistency_check(inputFile,ncFile,inputFilename,latcoord=None,loncoord=None,levcoord=None,tcoord=None,fix=False):
    print("====== Consistency check... ======")
    # Check that ancillary file is valid.
    inputFile = validate(inputFile,filename=inputFilename,fix=fix)
    nlat_in_each_var = [len(l) for l in get_latitude_each_var(inputFile)]
    nlon_in_each_var = [len(l) for l in get_longitude_each_var(inputFile)]
    lev_in_each_var, pseudo_in_each_var = get_levels_each_var(inputFile)
    has_pseudo_in_each_var = has_pseudo_each_var(inputFile)
    levels_in_each_var = [pseudo_in_each_var[ivar] if ps else lev_in_each_var[ivar] for ivar,ps in enumerate(has_pseudo_in_each_var)]
    
    # Check that the number of variables is consistent
    nvar_nc = len(ncFile.data_vars)
    nvar_ancil = len(lev_in_each_var)
    if nvar_nc != nvar_ancil:
        raise QValueError(f"Number of data variables not consistent!\n"
                f"Number of data variables in the ancillary file: {nvar_ancil}. "
                f"Number of data variables in the netCDF file: {nvar_nc}.")
    
    # Check that longitude, latitude and time coords are present in the .nc file and they have consistent lenghts with the ancillary file
    # Check latitude
    lat_out_each_var,latcoord = check_latitude(ncFile,latcoord=latcoord)
    # Check that latitude dimension is consistent
    if not regrid:
        for i,l in enumerate(lat_out_each_var):
            if len(l) != nlat_in_each_var[i]:
                raise QValueError(f"Latitude dimension not consistent for variable {i+1}!\nNumber of latitude points "
                    f"in netCDF file: {len(l)}. Number of latitude points in ancillary file: {nlat_in_each_var[i]}."
                    "\nIf you want to regrid the ancillary file onto the netCDF grid, please use the '--regrid' option.")

    # Check longitude
    lon_out_each_var,loncoord = check_longitude(ncFile,loncoord=loncoord)
    # Check that longitude dimension is consistent
    if not regrid:
        for i,l in enumerate(lon_out_each_var):
            if len(l) != nlon_in_each_var[i]:
                raise QValueError(f"Longitude dimension not consistent for variable {i+1}!\nNumber of longitude points "
                    f"in netCDF file: {len(l)}. Number of longitude points in ancillary file: {nlon_in_each_var[i]}."
                    "\nIf you want to regrid the ancillary file onto the netCDF grid, please use the '--regrid' option.")

    # Check levels
    levels_out_each_var,levcoord = check_level(ncFile,levcoord=levcoord)
    # Check that level dimension is consistent
    if not regrid:
        for i,l in enumerate(levels_out_each_var):
            if len(l) != len(lev_in_each_var[i]):
                raise QValueError(f"Level dimension not consistent for variable {i+1}!\nNumber of levels in netCDF file: {len(l)}."
                    f" Number of levels in ancillary file: {len(lev_in_each_var[i])}."
                    "\nIf you want to regrid the ancillary file onto the netCDF grid, please use the '--regrid' option.")

    # Check time
    t_out,tcoord = check_time(ncFile,tcoord=tcoord)
    ntime=len(t_out)
    # Check that time dimension is consistent
    if ntime != inputFile.integer_constants.num_times:
        raise QValueError(f"Time dimension not consistent!\nLength of netCDF file's time: {ntime}."
            f" Length of ancillary file's time: {inputFile.integer_constants.num_times}.")
    
    # Check that NC File doesn't have any additional variables
    for ivar,var in enumerate(ncFile.data_vars):
         ncdims = set(ncFile[var].dims)
         dims = set(filter(None,[tcoord,latcoord[ivar],loncoord[ivar],levcoord[ivar]]))
         if not ncdims == dims:
                raise QValueError("Different dimensions between the netCDF and ancillary file for "
                                  f"variable '{ncFile[var].name}'. NetCDF file dimensions: {ncdims}. "
                                  f"Ancillary file dimensions: {dims}.")

    print("====== Consistency check OK! ======")
    return lat_out_each_var, latcoord, lon_out_each_var, loncoord, levels_out_each_var, levcoord, ntime, tcoord, inputFile

def modify_and_write(inputFile,inputFilename,outputFilename,ncFile,regrid,lat_out_each_var,latcoord,lon_out_each_var,loncoord,lev_out,levcoord,ntime,tcoord,nanval):
    # WRITE FILE
    if outputFilename is None:
        outputFilename=inputFilename+"_modified"
        k=0
        while os.path.isfile(outputFilename):
            k+=1
            outputFilename = outputFilename+str(k)
    else:
        outputFilename = os.path.abspath(outputFilename)
    
    def _substitute_nanval(data,latc,lonc):
        if nanval is None:
            return data.where(data.notnull(),UM_NANVAL).transpose(latc,lonc).values
        else:
            return data.where(data != nanval, UM_NANVAL).transpose(latc,lonc).values

    def _select_time_level(data,levc,tc,lvind,tind):
        data = data.isel({tc:tind}, drop=True)
        if levcoord is not None:
            data = data.isel({levc:lvind}, drop=True)
        return data

    def _get_2d_data(data,latc,lonc,levc,tc,lvind,tind):
        return _substitute_nanval(_select_time_level(data,levc,tc,lvind,tind),latc,lonc).squeeze().astype(np.float64)

    if regrid:
        print(f"====== Regridding '{outputFilename}'... ======")
        newAncilFile = regrid_ancil(inputFile,lat_out_each_var,lon_out_each_var,lev_out)
        print(f"====== Regridding '{outputFilename}' OK! ======")
    else:
        # Create a copy of the ancillary file to modify
        newAncilFile = inputFile.copy(include_fields=True)

    print(f"====== Modifying and writing '{outputFilename}'... ======")

    fldind = iter(newAncilFile.fields)
    for t in range(ntime):
        for ivar,var in enumerate(ncFile.data_vars):
            for lv,_ in enumerate(lev_out[ivar]):
                data_2d = _get_2d_data(ncFile[var],latcoord[ivar],
                                       loncoord[ivar],levcoord[ivar],
                                       tcoord,lv,t)
                next(fldind).set_data_provider(mule.ArrayDataProvider(data_2d))

    newAncilFile.to_file(outputFilename)
    print(f"====== Writing '{outputFilename}' ancillary file OK! ======")

def main(inputFilename,ncFilename,outputFilename,latcoord,loncoord,levcoord,tcoord,nanval,regrid,fix):
        inputFile,ncFile = read_files(inputFilename,ncFilename)
        lat_out, latcoord, lon_out, loncoord, lev_out, levcoord, ntime, tcoord, inputFile = consistency_check(inputFile,ncFile,inputFilename,latcoord,loncoord,levcoord,tcoord,fix)
        modify_and_write(inputFile,inputFilename,outputFilename,ncFile,regrid,lat_out,latcoord,lon_out,loncoord,lev_out,levcoord,ntime,tcoord,nanval)

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
                        help="Name of the netCDF variables' latitude dimension. If the netCDF has different latitude "
                            "names for different variables, list of the latitude dimension names for every netCDF variable.")
    parser.add_argument('--lon', '--longitude', dest='longitude_name', required=False, type=str,
                        help="Name of the netCDF variables' longitude dimension. If the netCDF has different longitude "
                            "names for different variables, list of the longitude dimension names for every netCDF variable.")
    parser.add_argument('--lev', '--level', dest='level_name', required=False, type=str,
                        help="Name of the netCDF variables' vertical level (or pseudo-level) dimension. "
                            "If the netCDF has different level names for different variables, list of the level "
                            "dimension names for every netCDF variable. If a variable does not have any vertical "
                            "dimension, use 'None' as a level name for that variable.")
    parser.add_argument('-t', '--time', dest='time_name', required=False, type=str,
                        help='Name of the time dimension in the netCDF file.')
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
    import warnings
    warnings.filterwarnings("ignore")
    from umami.ancil_utils import (UM_NANVAL, read_ancil,get_latitude_each_var,get_longitude_each_var,
                                   get_levels_each_var,has_pseudo_each_var,regrid_ancil)
    from umami.netcdf_utils import (split_coord_names,read_netCDF,check_latitude, check_longitude,
                                    check_level,check_time)
    from umami.ancil_utils.validation_tools import validate
    from umami.quieterrors import QValueError

    # (inputFilename,ncFilename,outputFilename,latcoord,loncoord,
    #     levcoord,tcoord,nanval,regrid,fix) = (
    #     "/g/data/w40/dxd565/um-reosc-slab/ancil/vavqa.reosc.ancil",
    #     "/g/data/w40/sza565/ancil_data/vavqa.reosc.ancil.shiftANZ.nc",
    #     "/g/data3/tm70/dm5220/ancil/abhik/shifted/vavqa.reosc.ancil.shiftANZ",
    #     None,
    #     ['longitude','longitude','longitude','longitude_1','longitude','longitude'],
    #     ['surface'],
    #     None,
    #     None,
    #     False,
    #     True,
    #     )
    
    inputFilename=os.path.abspath(args.um_input_file)
    ncFilename=os.path.abspath(args.ncfile)
    outputFilename=args.um_output_file
    latcoord=split_coord_names(args.latitude_name)
    loncoord=split_coord_names(args.longitude_name)
    levcoord=split_coord_names(args.level_name)
    tcoord=args.time_name
    nanval=args.nanval
    regrid=args.regrid
    fix=args.fix

    print(f"====== Reading '{inputFilename}' ancillary file... ======")

    main(inputFilename,ncFilename,outputFilename,latcoord,loncoord,levcoord,
         tcoord,nanval,regrid,fix)




