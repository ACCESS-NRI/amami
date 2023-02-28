#!/usr/bin/env python

# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

# Script created by Davide Marchegiani (davide.marchegiani@anu.edu.au) at ACCESS-NRI.

from umami.quieterrors import QValueError
import xarray as xr
import numpy as np

def read_netCDF(inputNCFilename,**kwargs):
    def_keys=dict(decode_times=False,chunks=-1)
    def_keys.update(kwargs)
    return xr.open_dataset(inputNCFilename,**def_keys)
    
def _get_dim_name(inputNCFile,dim_names,errmsg):
    for dim in dim_names:
        if dim in inputNCFile.dims:
            return dim
    raise QValueError(errmsg)

def check_latitude(inputNCFile,latcoord=None):
    if latcoord is None: #If user has not defined any latitude name
        latcoord = _get_dim_name(inputNCFile,dim_names=('latitude','lat'),
            errmsg="No latitude dimension found in the netCDF file.\n"
                    "To specify the name of the latitude dimension in the netCDF "
                    "file use the '--latitude <name>' option.")
    elif latcoord not in inputNCFile.dims:
        raise QValueError(f"Specified latitude dimension '{latcoord}' not found in netCDF file.")
    return inputNCFile[latcoord].values,latcoord

def check_longitude(inputNCFile,loncoord=None):
    if loncoord is None: #If user has not defined any longitude name
            loncoord = _get_dim_name(inputNCFile,dim_names=('longitude','lon'),
                errmsg="No longitude dimension found in the netCDF file.\n"
                        "To specify the name of the longitude dimension in the netCDF "
                        "file use the '--longitude <name>' option.")
    elif loncoord not in inputNCFile.dims:
        raise QValueError(f"Specified longitude dimension '{loncoord}' not found in netCDF file.")
    return inputNCFile[loncoord].values,loncoord

def check_level(inputNCFile,has_pseudo,lev_in,levcoord=None):
    if levcoord is None: #If user has not defined any level name
        if any([(len(l)>1 and not has_pseudo[i]) for i,l in enumerate(lev_in)]):
            levcoord = _get_dim_name(inputNCFile,dim_names=("pressure","vertical_level"),
                errmsg="No vertical level dimension found in the netCDF file.\n"
                        "To specify the name of the vertical level dimension in the netCDF "
                        "file use the '--level <name>' option.")
            lev_out = [np.linspace(lev_in[ivar][0],lev_in[ivar][-1],len(inputNCFile[var][levcoord])).tolist() if (levcoord in inputNCFile[var].dims) and (len(inputNCFile[var][levcoord]) != len(lev_in[ivar])) else lev_in[ivar] for ivar,var in enumerate(inputNCFile.data_vars)]
        else:
            lev_out = lev_in.copy()
    elif levcoord not in inputNCFile.dims:
        raise QValueError(f"Specified vertical level dimension '{levcoord}' not found in netCDF file.")
    else:
        lev_out = [np.linspace(lev_in[ivar][0],lev_in[ivar][-1],len(inputNCFile[var][levcoord])).tolist() if (levcoord in inputNCFile[var].dims) and (len(inputNCFile[var][levcoord]) != len(lev_in[ivar])) else lev_in[ivar] for ivar,var in enumerate(inputNCFile.data_vars)]
    return lev_out,levcoord

def check_pseudo(inputNCFile,has_pseudo,pseudo_in,pseudocoord=None):
    if pseudocoord is None: #If user has not defined any pseudo-level name
        if any(has_pseudo): #If there are any pseudo-levels in the ancil file
            pseudocoord = _get_dim_name(inputNCFile,dim_names=("pseudo_level","pseudo"),
                errmsg="Pseudo-levels found in the ancillary file, but no pseudo-level dimension found in the netCDF file.\n"
                        "To specify the name of the pseudo-level dimension in the netCDF "
                        "file use the '--pseudo <name>' option.")
            pseudo_out = [np.linspace(pseudo_in[ivar][0],pseudo_in[ivar][-1],len(inputNCFile[var][pseudocoord])).tolist() if (pseudocoord in inputNCFile[var].dims) and (len(inputNCFile[var][pseudocoord]) != len(pseudo_in[ivar])) else pseudo_in[ivar] for ivar,var in enumerate(inputNCFile.data_vars)]
        else:
            pseudo_out = pseudo_in.copy()
    elif pseudocoord not in inputNCFile.dims: #If user defiined pseudo-level name but no it doesn't exist in the netCDF file
        raise QValueError(f"Specified pseudo-level dimension '{pseudocoord}' not found in netCDF file.")
    else: #If user defined pseudo-level name and it exists in the netCDF file
        pseudo_out = [np.linspace(pseudo_in[ivar][0],pseudo_in[ivar][-1],len(inputNCFile[var][pseudocoord])).tolist() if (pseudocoord in inputNCFile[var].dims) and (len(inputNCFile[var][pseudocoord]) != len(pseudo_in[ivar])) else pseudo_in[ivar] for ivar,var in enumerate(inputNCFile.data_vars)]
    return pseudo_out,pseudocoord

def check_time(inputNCFile,tcoord=None):
    if tcoord is None: #If user has not defined any longitude name
        tcoord = _get_dim_name(inputNCFile,dim_names=('time','t'),
            errmsg="No time dimension found in the netCDF file.\n"
                    "To specify the name of the time dimension in the netCDF "
                    "file use the '--time <name>' option.")
    elif tcoord not in inputNCFile.dims:
        raise QValueError(f"Specified longitude dimension '{tcoord}' not found in netCDF file.")
    return inputNCFile[tcoord].values,tcoord
    