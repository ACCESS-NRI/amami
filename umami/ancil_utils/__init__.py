# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

# Script created by Davide Marchegiani (davide.marchegiani@anu.edu.au) at ACCESS-NRI.

import mule
import itertools
import numpy as np
from scipy.interpolate import interpn
import os
from umami.quieterrors import QValueError, QFileExistsError

UM_NANVAL=-1073741824.0 #(-2.0**30)

def get_stash_each_var(ancilFile):
    return list(dict.fromkeys([f.lbuser4 for f in ancilFile.fields]))

def get_latitude(ancilFile):
    f = ancilFile.fields[0].copy()
    return np.linspace(f.bzy+f.bdy,
                       f.bzy+f.bdy+f.bdy*(f.lbrow-1),
                       f.lbrow)

def get_longitude(ancilFile):
    f = ancilFile.fields[0].copy()
    return np.linspace(f.bzx+f.bdx,
                       f.bzx+f.bdx+f.bdx*(f.lbnpt-1),
                       f.lbnpt)

def get_levels_each_var(ancilFile):
    '''Gets the vertical level or pseudo-level values for each variable in the ancillary file ancilFile.'''
    first_timestep_fields = ancilFile.fields[:(len(ancilFile.fields)//(ancilFile.integer_constants.num_times))].copy()
    # Get stash codes to group into different variables
    stash = [f.lbuser4 for f in first_timestep_fields]
    # Get levels
    levs=[[f.blev for f in first_timestep_fields],
          [f.lbuser5 for f in first_timestep_fields],
          [f.lblev for f in first_timestep_fields]]
    # Separate levels for each ancil file variable
    levels = dict()
    all_levels = []
    for lv in levs:
        for st,lvl in zip(stash,lv):
            if st in levels:
                levels[st].append(lvl)
            else:
                levels[st] = [lvl]
        all_levels.append(list(levels.values()))
        levels=dict()
    return all_levels

def has_pseudo_levels_each_var(ancilFile):
    '''Returns a list of bool, with each one being True if the variable has pseudo-levels, False otherwise, for every variable in the ancillary file ancilFile.'''
    first_timestep_fields = ancilFile.fields[:(len(ancilFile.fields)//(ancilFile.integer_constants.num_times))].copy()
    # Get stash codes to group into different variables
    stash = [f.lbuser4 for f in first_timestep_fields]
    # Get pseudo-levels
    pslevs = [f.lbuser5 for f in first_timestep_fields]
    # Separate levels for each ancil file variable
    levels=dict()
    for st,lv in zip(stash,pslevs):
        if st in levels:
            levels[st].append(lv)
        else:
            levels[st] = [lv]
    return [sum(l)!=0 for l in levels.values()]

def read_ancil(ancilFilename):
    ancilFilename = os.path.abspath(ancilFilename)
    if not os.path.isfile(ancilFilename):
        raise QFileExistsError(f"Ancillary file '{ancilFilename}' does not exist.")
    try:
        file = mule.load_umfile(ancilFilename)
    except ValueError:
        raise QValueError(f"'{ancilFilename}' does not appear to be a valid UM ancillary file.")
    else:
        if not isinstance(file,mule.ancil.AncilFile):
            raise QValueError(f"'{ancilFilename}' does not appear to be a valid UM ancillary file.")
    return file

def regrid_ancil(inputFile,lat_out=None,lon_out=None,lev_out_each_var=None,method=None):
    '''
    Regrids a UM ancilFile over latitude, longitude and UM vertical levels, using scipy.interpolate.interpn function.

    PARAMETERS
    -   ancilFile is a mule.ancilFile
    -   lat_out is an array-like variable with the output latitude coordinate. If set to None, no regridding will
        be performed over latitude.
    -   lon_out is an array-like variable with the output longitude coordinate. If set to None, no regridding will
        be performed over longitude.
    -   lev_out is a list of array-like variables with the output vertical level coordinate fpr each variable in ancilFile. 
        If set to None, no regridding will be performed over vertical levels.
    -   method is a string defining the interpolation method. Methods supported are 'linear', 'nearest', 'cubic', 'quintic' and 'pchip'.
        If set to None, 'linear' interpolation is used.
    '''
    # Check method
    avail_methods=('linear', 'nearest', 'cubic', 'quintic', 'pchip')
    if method is None:
        method = 'linear'
    elif method not in avail_methods:
        raise QValueError(f"'method' needs to be one in {avail_methods}. You provided {method}.")

    # Parse input file
    if not isinstance(inputFile,mule.AncilFile):
        raise TypeError("'ancilFile' needs to be a mule.ancilFile object.")
    # Get the input coordinates from the first field of the ancilFile
    f=inputFile.fields[0].copy()
    lat_in = get_latitude(inputFile)
    lon_in = get_longitude(inputFile)
    lev_in_each_var,pseudo_each_var,lblev_each_var = get_levels_each_var(inputFile)
    ntimes = inputFile.integer_constants.num_times
    lbegin = f.lbegin
    stash_each_var = get_stash_each_var(inputFile)
    # Parse output coords 
    # Latitude
    if lat_out is None:
        lat_out = lat_in
    elif isinstance(lat_out,(int, float)) and not isinstance(lat_out, bool):
        lat_out = [lat_out]
    elif not hasattr(lat_out,'__iter__'):
        raise TypeError("'lat_out' needs to be an iterable.")
    # Longitude
    if lon_out is None:
        lon_out = lon_in
    elif isinstance(lon_out,(int, float)) and not isinstance(lon_out, bool):
        lon_out = [lon_out]
    elif not hasattr(lon_out,'__iter__'):
        raise TypeError("'lon_out' needs to be an iterable.")
    # Vertical levels
    if lev_out_each_var is None:
        lev_out_each_var = lev_in_each_var.copy()
    elif not isinstance(lev_out_each_var,list) or not all([hasattr(l,'__iter__') for l in lev_out_each_var]):
        raise TypeError("'lev_out' needs to be a list of iterables.")
    # Check that if var has pseudo-levels, the lev_out is consistent
    has_pseudo = has_pseudo_levels_each_var(inputFile)
    lev_outpoints = lev_out_each_var.copy()
    for ivar,hp in enumerate(has_pseudo):
        if hp:
            if lev_out_each_var[ivar] != lev_in_each_var[ivar]:
                raise ValueError(f"Pseudo-level regridding not supported. Pseudo-levels found in the variable n.{ivar+1} of "
                                  "the ancillary file, but the output levels are not equal to the input ones.")
            else:
                lev_in_each_var[ivar] = pseudo_each_var[ivar]
                lev_outpoints[ivar] = pseudo_each_var[ivar]
    if all(has_pseudo):
        num_levels_out = inputFile.integer_constants.num_levels
    else:
        for ivar,hp in enumerate(has_pseudo): 
            if not hp:
                num_levels_out = len(lev_out_each_var[ivar])
                break

    nlat_out = len(lat_out)
    nlon_out = len(lon_out)
    nlev_out_each_var = list(map(len,lev_out_each_var))
    if len(lat_out) > 1:
        dlat_out = lat_out[1] - lat_out[0]
    else:
        dlat_out = 180.
    if len(lon_out) > 1:
        dlon_out = lon_out[1] - lon_out[0]
    else:
        dlon_out = 360.
    
    # Define regridding output points
    outpoints_each_var = [list(itertools.product(lat_out,lon_out,l)) for l in lev_outpoints]

    # Regrid and get new fields
    f = iter(inputFile.fields.copy())
    interp_data = []
    for _ in range(ntimes): # Loop for each timestep
        for ivar,lvls in enumerate(lev_in_each_var): # Loop for each variable
            data = []
            for _ in lvls: # Loop for each level
                data.append(next(f).get_data())
            data = np.stack(data, axis=-1)
            data = np.where(data == UM_NANVAL,np.nan,data)
            interp_data.append(interpn((lat_in,lon_in,lvls), data, outpoints_each_var[ivar], 
                bounds_error=False, fill_value=None, method=method).reshape(nlat_out,nlon_out,nlev_out_each_var[ivar]))
    newfields = np.concatenate(interp_data,axis=-1)
    newfields = np.where(np.isnan(newfields),UM_NANVAL,newfields)

    # Create new ancil file 
    regriddedFile = inputFile.copy(include_fields=False)
    # Change regridded file header
    regriddedFile.integer_constants.num_rows = nlat_out
    regriddedFile.integer_constants.num_cols = nlon_out
    regriddedFile.integer_constants.num_levels = num_levels_out
    regriddedFile.real_constants.start_lat = lat_out[0]
    regriddedFile.real_constants.start_lon = lon_out[0]
    regriddedFile.real_constants.north_pole_lat = lat_out[-1]
    regriddedFile.real_constants.north_pole_lon = lon_out[-1]
    regriddedFile.real_constants.row_spacing = dlat_out
    regriddedFile.real_constants.col_spacing = dlon_out
    # If the grid is a global one, force polar values to be the zonal means
    if (inputFile.fixed_length_header.horiz_grid_type == 0 and 
        np.allclose(lat_out[0], -90) and
        np.allclose(lon_out[0], 0)):
        newfields[0,...]=newfields[0,...].mean(axis=0)
        newfields[-1,...]=newfields[-1,...].mean(axis=0)

    # Assign new fields to new ancil file
    fit=iter(newfields.transpose(2,0,1))
    for _ in range(ntimes): # Loop for each timestep
        for ivar,lvls in enumerate(lev_out_each_var): # Loop for each variable
            for ilvl,lev in enumerate(lvls): # Loop for each level
                regriddedFile.fields.append(inputFile.fields[0].copy())
                f = regriddedFile.fields[-1]
                # Change field headers
                f.lblrec = nlat_out*nlon_out
                f.lbrow = nlat_out
                f.lbnpt = nlon_out
                f.lbegin = lbegin + f.lbnrec*(len(regriddedFile.fields)-1)
                f.lblev = lblev_each_var[ivar][ilvl]
                f.lbuser2 = 1+f.lblrec*(len(regriddedFile.fields)-1)
                f.lbuser4 = stash_each_var[ivar]
                f.lbuser5 = pseudo_each_var[ivar][ilvl]
                f.blev = lev    
                f.bzy = lat_out[0] - dlat_out
                f.bdy = dlat_out
                f.bzx = lon_out[0] - dlon_out
                f.bdx = dlon_out
                f.set_data_provider(mule.ArrayDataProvider(next(fit)))
    return regriddedFile