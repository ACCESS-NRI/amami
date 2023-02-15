# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

import mule
import itertools
import numpy as np
from scipy.interpolate import interpn
import sys
import os

UM_NANVAL=-1073741824.0 #(-2.0**30)

def read_ancil(ancilFilename):
    ancilFilename = os.path.abspath(ancilFilename)
    if not os.path.isfile(ancilFilename):
        sys.exit(f"Ancillary file '{ancilFilename}' does not exist.")
    try:
        file = mule.load_umfile(ancilFilename)
    except ValueError:
        sys.exit(f"'{ancilFilename}' does not appear to be a valid UM ancillary file.")
    else:
        if not isinstance(file,mule.ancil.AncilFile):
            sys.exit(f"'{ancilFilename}' does not appear to be a valid UM ancillary file.")
    return file

def regrid_ancil(inputFile,lat_out=None,lon_out=None,nlev_out=None):
    '''
    Regrids a UM ancilFile over latitude, longitude and UM vertical levels, using scipy.interpolate.interpn function.

    PARAMETERS
    - ancilFile is a mule.ancilFile
    - lat_out is an array-like variable with the output latitude coordinate. If set to None, no regridding will
      be performed over latitude.
    - lon_out is an array-like variable with the output longitude coordinate. If set to None, no regridding will
      be performed over longitude.
    - nlev_out is an integer with the the number of vertical levels in output. If set to None, no regridding 
      will be performed over vertical levels. Pseudo-levels are not counted as vertical levels and regridding
      will not be performed for pseudo-levels. If ancilFile has pseudo-levels, nlev_out needs to be 1.
    '''

    # Parse input file
    if not isinstance(inputFile,mule.AncilFile):
        raise TypeError("'ancilFile' needs to be a mule.ancilFile object.")
    # Get the input coordinates from the first field of the ancilFile
    f=inputFile.fields[0].copy()
    lat_in = np.linspace(f.bzy+f.bdy,
                        f.bzy+f.bdy+f.bdy*(inputFile.integer_constants.num_rows-1),
                        inputFile.integer_constants.num_rows)
    lon_in = np.linspace(f.bzx+f.bdx,
                        f.bzx+f.bdx+f.bdx*(inputFile.integer_constants.num_cols-1),
                        inputFile.integer_constants.num_cols)
    lev_in = np.arange(1,inputFile.integer_constants.num_levels+1)
    ntimes = inputFile.integer_constants.num_times
    lbegin = f.lbegin
    # Check if ancil file has pseudolevs
    first_fields = inputFile.fields[:(len(inputFile.fields)//(ntimes*inputFile.integer_constants.num_levels))].copy()
    npseudoLevs_per_var = [f.lbuser5 for i,f in enumerate(first_fields[:-1]) if f.lbuser5==0 or first_fields[i+1].lbuser5<first_fields[i].lbuser5]+[first_fields[-1].lbuser5]
    if sum(npseudoLevs_per_var) != 0 and nlev_out != 1:
        raise ValueError("Pseudo-levels found in the ancilFile, but 'nlev_out' is not 1.")
    else:
        npseudoLevs_per_var = [l+1 if l == 0 else l for l in npseudoLevs_per_var]
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
    if nlev_out is None:
        lev_out = lev_in        
    elif not isinstance(nlev_out,int):
        raise TypeError("'nlev_out' needs to be an integer.")
    else:
        lev_out = np.linspace(1,inputFile.integer_constants.num_levels,nlev_out)
    
    nlat_out = len(lat_out)
    nlon_out = len(lon_out)
    if len(lat_out) > 1:
        dlat_out = lat_out[1] - lat_out[0]
    else:
        dlat_out = 180.
    if len(lon_out) > 1:
        dlon_out = lon_out[1] - lon_out[0]
    else:
        dlon_out = 360.
    
    outpoints = list(itertools.product(lat_out,lon_out,lev_out))
    
    # Create new ancil file 
    regriddedFile = inputFile.copy(include_fields=False)
    # Change regridded file header
    regriddedFile.integer_constants.num_rows = nlat_out
    regriddedFile.integer_constants.num_cols = nlon_out
    regriddedFile.integer_constants.num_levels = nlev_out
    regriddedFile.real_constants.start_lat = lat_out[0]
    regriddedFile.real_constants.start_lon = lon_out[0]
    regriddedFile.real_constants.north_pole_lat = lat_out[-1]
    regriddedFile.real_constants.north_pole_lon = lon_out[-1]
    regriddedFile.real_constants.row_spacing = dlat_out
    regriddedFile.real_constants.col_spacing = dlon_out

    f = 0
    interp=[]
    while f < len(inputFile.fields):
        data = []
        for _ in range(inputFile.integer_constants.num_levels):
            data.append(inputFile.fields[f].copy().get_data())
            f += 1
        values = np.stack(data,axis=2)
        interp.append(interpn((lat_in,lon_in,lev_in), values, outpoints, bounds_error=False, fill_value=None).reshape(nlat_out,nlon_out,nlev_out))
    newfields = np.stack(interp,axis=3).reshape(nlat_out,nlon_out,-1)
    # If the grid is a global one, force polar values to be the zonal means
    if (inputFile.fixed_length_header.horiz_grid_type == 0 and 
        np.allclose(lat_out[0], -90) and
        np.allclose(lon_out[0], 0)):
        newfields[0,...]=newfields[0,...].mean(axis=0)
        newfields[-1,...]=newfields[-1,...].mean(axis=0)

    # Regrid
    k=0
    # Create indeces of first new variable
    varind = [[f.lbuser4 for f in inputFile.fields].index(k) for k in dict.fromkeys([f.lbuser4 for f in inputFile.fields]).keys()]
    for _ in range(ntimes):
        for ips,nps in enumerate(npseudoLevs_per_var):
            for lev in range(nlev_out):
                for l in range(1,nps+1):
                    regriddedFile.fields.append(inputFile.fields[varind[ips]].copy())
                    f = regriddedFile.fields[k]
                    # Change field pseudo-level
                    if len(npseudoLevs_per_var) > 1:
                        f.lbuser5 = l
                    else:
                        f.lbuser5 = 0
                    # Change field headers relative to coordinates
                    f.lblrec = nlat_out*nlon_out
                    f.lbuser2 = 1+(f.lblrec*k)
                    f.lbegin = lbegin + (f.lbnrec*k)
                    f.lbrow = nlat_out
                    f.lbnpt = nlon_out
                    f.bdy = dlat_out
                    f.bdx = dlon_out
                    f.bzy = lat_out[0] - dlat_out
                    f.bzx = lon_out[0] - dlon_out
                    f.lblev = lev + 1
                    f.blev = lev + 1 #MODIFY!!!!!!!!!
                    f.set_data_provider(mule.ArrayDataProvider(newfields[:,:,k]))
                    k+=1
    return regriddedFile

