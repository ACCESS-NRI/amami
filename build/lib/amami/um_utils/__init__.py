# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

# Script created by Davide Marchegiani (davide.marchegiani@anu.edu.au) at ACCESS-NRI.

import mule
import itertools
import numpy as np
from scipy.interpolate import interpn
import os
from amami.quieterrors import QValueError, QFileNotFoundError

UM_NANVAL=-1073741824.0 #(-2.0**30)

def get_stash_each_var(umFile):
    return list(dict.fromkeys([f.lbuser4 for f in umFile.fields]))

def _first_timestep_fields(umFile):
    return umFile.fields[:(len(umFile.fields)//(umFile.integer_constants.num_times))].copy()

def get_latitude_each_var(umFile):
    '''Gets the latitude for each variable in the UM file umFile.'''
    first_timestep_fields = _first_timestep_fields(umFile)
    # Get stash codes to group into different variables
    stash = [f.lbuser4 for f in first_timestep_fields]
    func=lambda f: np.linspace(f.bzy+f.bdy,
                    f.bzy+f.bdy+f.bdy*(f.lbrow-1),
                    f.lbrow).tolist()
    lat = (func(f) if (i==0 or stash[i]!=stash[i-1]) else None for i,f in enumerate(first_timestep_fields))
    return list(filter(None,lat))

def get_longitude_each_var(umFile):
    '''Gets the longitude for each variable in the UM file umFile.'''
    first_timestep_fields = _first_timestep_fields(umFile)
    # Get stash codes to group into different variables
    stash = [f.lbuser4 for f in first_timestep_fields]
    func=lambda f: np.linspace(f.bzx+f.bdx,
                    f.bzx+f.bdx+f.bdx*(f.lbnpt-1),
                    f.lbnpt).tolist()
    lon = (func(f) if (i==0 or stash[i]!=stash[i-1]) else None for i,f in enumerate(first_timestep_fields))
    return list(filter(None,lon))

def get_levels_each_var(umFile):
    '''Gets the vertical levels and pseudo-levels for each variable in the UM file umFile.'''
    first_timestep_fields = _first_timestep_fields(umFile)
    # Get stash codes to group into different variables
    stash = [f.lbuser4 for f in first_timestep_fields]
    # Get levels
    levs=[f.blev for f in first_timestep_fields]
    pseudo=[f.lbuser5 for f in first_timestep_fields]
    levels=[]
    for lvl in (levs,pseudo):
        levels.append([])
        for i,l in enumerate(lvl):
            if i==0 or stash[i]!=stash[i-1]:
                levels[-1].append([l])
            else:
                levels[-1][-1].append(l)
    return levels

def _get_lblev_each_var(umFile):
    '''Gets the vertical level codes (lblev) for each variable in the UM file umFile.'''
    first_timestep_fields = _first_timestep_fields(umFile)
    # Get stash codes to group into different variables
    stash = [f.lbuser4 for f in first_timestep_fields]
    # Get lblevs
    lblev = [f.lblev for f in first_timestep_fields]
    levels=[]
    for i,l in enumerate(lblev):
        if i==0 or stash[i]!=stash[i-1]:
            levels.append([l])
        else:
            levels[-1].append(l)
    return levels

def has_pseudo_each_var(umFile):
    '''Returns a list of bool, with each one being True if the variable has pseudo-levels, False otherwise, for every variable in the UM file umFile.'''
    return [sum(l)!=0 for l in get_levels_each_var(umFile)[1]]

def read_fieldsfile(umFilename,check_ancil=True):
    umFilename = os.path.abspath(umFilename)
    if not os.path.isfile(umFilename):
        raise QFileNotFoundError(f"'{umFilename}' does not exist.")
    try:
        file = mule.load_umfile(umFilename)
        file.remove_empty_lookups()
    except ValueError:
        raise QValueError(f"'{umFilename}' does not appear to be a UM file.")
    if (check_ancil) and (not isinstance(file,mule.ancil.AncilFile)):
        raise QValueError(f"'{umFilename}' does not appear to be a UM ancillary file.")
    return file

def regrid_fieldsfile(umFile,lat_out_each_var=None,lon_out_each_var=None,lev_out_each_var=None,method=None):
    '''
    Regrids a UM file over latitude, longitude and UM vertical levels, using scipy.interpolate.interpn function.

    PARAMETERS
    -   umFile is a mule.FieldsFile
    -   lat_out is a list of array-like variables with the output latitude coordinate. If set to None, no regridding will
        be performed over latitude.
    -   lon_out is a list of array-like variables with the output longitude coordinate. If set to None, no regridding will
        be performed over longitude.
    -   lev_out is a list of array-like variables with the output vertical level coordinate for each variable in ancilFile. 
        If set to None, no regridding will be performed over vertical levels.
    -   method is a string defining the interpolation method. Methods supported are 'linear', 'nearest', 'cubic', 'quintic' and 'pchip'.
        If set to None, 'nearest' interpolation is used.
    '''
    # Check method
    avail_methods=('linear', 'nearest', 'cubic', 'quintic', 'pchip')
    if method is None:
        method = 'nearest'
    elif method not in avail_methods:
        raise QValueError(f"'{method}' method not recognized. method needs to be one in {avail_methods}.")

    # Parse input file
    if not isinstance(umFile,mule.AncilFile):
        raise TypeError("'ancilFile' needs to be a mule.ancilFile object.")
    # Get the input coordinates from the first field of the ancilFile
    f=umFile.fields[0].copy()
    lat_in_each_var = get_latitude_each_var(umFile)
    lon_in_each_var = get_longitude_each_var(umFile)
    lev_in_each_var,pseudo_in_each_var = get_levels_each_var(umFile)
    lblev_in_each_var = _get_lblev_each_var(umFile)
    ntimes = umFile.integer_constants.num_times
    stash_each_var = get_stash_each_var(umFile)
    has_pseudo_in_each_var = has_pseudo_each_var(umFile)
    # Mix pseudo-levels and normal levels
    levels_in_each_var = [pseudo_in_each_var[ivar] if ps else lev_in_each_var[ivar] for ivar,ps in enumerate(has_pseudo_in_each_var)]
    # Parse output coords 
    # Latitude
    if lat_out_each_var is None:
        lat_out_each_var = lat_in_each_var
    elif not isinstance(lat_out_each_var,list) or not all([hasattr(l,'__iter__') for l in lat_out_each_var]):
        raise TypeError("'lat_out_each_var' needs to be a list of iterables.")
    # Longitude
    if lon_out_each_var is None:
        lon_out_each_var = lon_in_each_var
    elif not isinstance(lon_out_each_var,list) or not all([hasattr(l,'__iter__') for l in lon_out_each_var]):
        raise TypeError("'lon_out_each_var' needs to be a list of iterables.")
    # Vertical levels
    if lev_out_each_var is None:
        lev_out_each_var = levels_in_each_var.copy()
    elif not isinstance(lev_out_each_var,list) or not all([hasattr(l,'__iter__') for l in lev_out_each_var]):
        raise TypeError("'lev_out' needs to be a list of iterables.")
    
    # Get num_levels
    if all(has_pseudo_in_each_var):
        num_levels_out = umFile.integer_constants.num_levels
    else:
        for ivar,hp in enumerate(has_pseudo_in_each_var): 
            if not hp:
                num_levels_out = len(lev_out_each_var[ivar])
                break

    nlat_out_each_var = [len(l) for l in lat_out_each_var]
    nlon_out_each_var = [len(l) for l in lon_out_each_var]
    nlev_out_each_var = [len(l) for l in lev_out_each_var]
    
    # Check that both InputFile and gridFile are consistent in case latitude, longitude or levels are of length 1
    # Check Latitude
    for ivar,nlo in enumerate(nlat_out_each_var):
        if ((len(lat_in_each_var[ivar]) == 1) and (nlo != 1)) or ((len(lat_in_each_var[ivar]) != 1) and (nlo == 1)):
            raise QValueError(f"Impossible to perform the interpolation from multiple points into one single point or vice-versa.\n"
                              f"Variable {ivar+1} of the input file has {len(lat_in_each_var[ivar])} latitude point(s). "
                              f"Variable {ivar+1} of the grid file has {nlo} latitude point(s).")
    # Check Longitude
    for ivar,nlo in enumerate(nlon_out_each_var):
        if ((len(lon_in_each_var[ivar]) == 1) and (nlo != 1)) or ((len(lon_in_each_var[ivar]) != 1) and (nlo == 1)):
            raise QValueError(f"Impossible to perform the interpolation from multiple points into one single point or vice-versa.\n"
                              f"Variable {ivar+1} of the input file has {len(lon_in_each_var[ivar])} longitude point(s). "
                              f"Variable {ivar+1} of the grid file has {nlo} longitude point(s).")
    # Check Level
    for ivar,olev in enumerate(nlev_out_each_var):
        if ((len(levels_in_each_var[ivar]) == 1) and (olev != 1)) or (((len(levels_in_each_var[ivar]) != 1) and (olev == 1))):
            raise QValueError(f"Impossible to perform the interpolation from multiple points into one single point or vice-versa.\n"
                              f"Variable {ivar+1} of the input file has {len(levels_in_each_var[ivar])} level(s). "
                              f"Variable {ivar+1} of the grid file has {olev} level(s).")

    dlat_out_each_var = [l[1]-l[0] if len(l)> 1 else 180. for l in lat_out_each_var]
    dlon_out_each_var = [l[1]-l[0] if len(l)> 1 else 180. for l in lon_out_each_var]
    
    # Define regridding output points
    outpoints_each_var = [list(itertools.product(lat,lon,lev)) for lat,lon,lev in zip(lat_out_each_var,lon_out_each_var,lev_out_each_var)]

    # Regrid and get new fields
    f = iter(umFile.fields.copy())
    interp_data = []
    for _ in range(ntimes): # Loop for each timestep
        for ivar,lvls in enumerate(levels_in_each_var): # Loop for each variable
            data = []
            for _ in lvls: # Loop for each level
                data.append(next(f).get_data())
            data = np.stack(data, axis=-1)
            data = np.where(data == UM_NANVAL,np.nan,data)
            interp_data.append(interpn((lat_in_each_var[ivar],lon_in_each_var[ivar],lvls), data, outpoints_each_var[ivar], 
                bounds_error=False, fill_value=None, method=method).reshape(nlat_out_each_var[ivar],nlon_out_each_var[ivar],nlev_out_each_var[ivar]))
    newfields = np.concatenate(interp_data,axis=-1)
    newfields = np.where(np.isnan(newfields),UM_NANVAL,newfields)

    # If the grid is a global one, force polar values to be the zonal means
    if (umFile.fixed_length_header.horiz_grid_type == 0 and 
        np.allclose(lat_out_each_var[0][0], -90) and
        np.allclose(lon_out_each_var[0][0], 0)):
        newfields[0,...]=newfields[0,...].mean(axis=0)
        newfields[-1,...]=newfields[-1,...].mean(axis=0)

    # Create new ancil file 
    regriddedFile = umFile.copy(include_fields=False)
    # Change regridded file header
    regriddedFile.integer_constants.num_rows = nlat_out_each_var[0]
    regriddedFile.integer_constants.num_cols = nlon_out_each_var[0]
    regriddedFile.integer_constants.num_levels = num_levels_out
    regriddedFile.real_constants.start_lat = lat_out_each_var[0][0]
    regriddedFile.real_constants.start_lon = lon_out_each_var[0][0]
    regriddedFile.real_constants.north_pole_lat = lat_out_each_var[0][-1]
    regriddedFile.real_constants.north_pole_lon = lon_out_each_var[0][-1]
    regriddedFile.real_constants.row_spacing = dlat_out_each_var[0]
    regriddedFile.real_constants.col_spacing = dlon_out_each_var[0]
    regriddedFile.fixed_length_header.data_start = np.int64(2049)

    # Assign new fields to new ancil file
    count = itertools.count()
    for _ in range(ntimes): # Loop for each timestep
        for ivar,lvls in enumerate(lev_out_each_var): # Loop for each variable
            for ilvl,lev in enumerate(lvls): # Loop for each level
                c = next(count)
                regriddedFile.fields.append(umFile.fields[0].copy())
                f = regriddedFile.fields[-1]
                # Change field headers
                f.lbpack = np.int64(0)
                f.lblrec = np.int64(nlat_out_each_var[ivar]*nlon_out_each_var[ivar])
                f.lbrow = np.int64(nlat_out_each_var[ivar])
                f.lbnpt = np.int64(nlon_out_each_var[ivar])
                f.lbegin = np.int64(2048 + f.lbnrec*c)
                f.lblev = np.int64(7777) if all(lbl == 7777 for lbl in lblev_in_each_var[ivar]) else \
                    np.int64(8888) if all(lbl == 8888 for lbl in lblev_in_each_var[ivar]) else \
                    np.int64(9999) if all(lbl == 9999 for lbl in lblev_in_each_var[ivar]) else \
                    np.int64(ilvl+1)
                f.lbuser2 = np.int64(1+f.lblrec*c)
                f.lbuser4 = np.int64(stash_each_var[ivar])
                f.lbuser5 = np.int64(lev if has_pseudo_in_each_var[ivar] else 0)
                f.blev = np.int64(lev if not has_pseudo_in_each_var[ivar] else 0)
                f.bzy = np.int64(lat_out_each_var[ivar][0] - dlat_out_each_var[ivar])
                f.bdy = np.int64(dlat_out_each_var[ivar])
                f.bzx = np.int64(lon_out_each_var[ivar][0] - dlon_out_each_var[ivar])
                f.bdx = np.int64(dlon_out_each_var[ivar])
                f.set_data_provider(mule.ArrayDataProvider(newfields[...,c].astype(np.float64)))
    return regriddedFile
