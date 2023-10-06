# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

# Script created by Davide Marchegiani (davide.marchegiani@anu.edu.au) at ACCESS-NRI.

from amami.quieterrors import QValueError, QParseError
import xarray as xr
import numpy as np

def split_coord_names(coordname):
    if coordname is None:
        return None
    elif ((coordname.startswith("[") or coordname.startswith("(")) and 
        not (coordname.endswith("]") or coordname.endswith(")"))) or \
       (not (coordname.startswith("[") or coordname.startswith("(")) and 
        (coordname.endswith("]") or coordname.endswith(")"))):
            raise QParseError("Bad coordinate name formatting. Coordinate name needs to be a single string, "
                              "or multiple strings separated by a comma. Parenthesis are allowed before the "
                              "first string and after the last one.\nExample: '[coord_name1,...,coord_nameN]' "
                              "or '(coord_name1,...,coord_nameN)' or 'coord_name1,...,coord_nameN'.")
    elif coordname.startswith("["):
        coordname = coordname[1:-1]
    return [s.strip() for s in coordname.split(",")]

def read_netCDF(inputNCFilename,remove_bnds=True,**kwargs):
    def_keys=dict(decode_times=False)
    def_keys.update(kwargs)
    nc = xr.open_dataset(inputNCFilename,**def_keys)
    if remove_bnds:
        # Remove any boundary variables (such as lat_bnds, lon_bnds) as well as latitude_longitude.
        nc = nc.drop([v for v in nc if (v=="latitude_longitude") or (v.endswith('_bnds'))])
    return nc
    
def _get_dim_name(inputNCFile,dim_name):
    for var in inputNCFile.data_vars:
        if dim_name not in inputNCFile[var].dims:
            raise QValueError(f"No '{dim_name}' dimension found in the netCDF file's variable '{inputNCFile[var].name}'.\n"
                f"To specify the name of the {dim_name} dimension(s) in the netCDF file use the '--{dim_name} <name>' option, "
                f"or '--{dim_name} [<name_{dim_name}_var1>,...,<name_{dim_name}_varN>]' in case the netCDF variables have different {dim_name} dimension "
                "names.")
    return [dim_name for _ in inputNCFile.data_vars]

def check_latitude(inputNCFile,latcoord=None):
    if latcoord is None: #If user has not defined any latitude name
        latcoord = _get_dim_name(inputNCFile,dim_name='latitude')
    elif len(latcoord)==1 and (len(latcoord) != len(inputNCFile.data_vars)):
         latcoord = np.repeat(latcoord,len(inputNCFile.data_vars),axis=0).tolist()
    elif (len(latcoord) != len(inputNCFile.data_vars)):
        raise QValueError(f"The length of the specified latitude dimension names needs to be "
                          "equal to the number of netCDF data variables.\nLength of the specified latitude "
                          f"dimension names: {len(latcoord)}, number of netCDF data variables: {len(inputNCFile.data_vars)}.")
    latval=[]    
    for lc,var in zip(latcoord,inputNCFile.data_vars):
        if lc not in inputNCFile[var].dims:
            raise QValueError(f"Specified latitude dimension '{lc}' not found in netCDF file's variable '{inputNCFile[var].name}'.")
        else:
            latval.append(inputNCFile[var][lc].values.tolist())
    return latval,latcoord

def check_longitude(inputNCFile,loncoord=None):
    if loncoord is None: #If user has not defined any longitude name
        loncoord = _get_dim_name(inputNCFile,dim_name='longitude')
    elif len(loncoord)==1 and (len(loncoord) != len(inputNCFile.data_vars)):
         loncoord = np.repeat(loncoord,len(inputNCFile.data_vars),axis=0).tolist()
    elif (len(loncoord) != len(inputNCFile.data_vars)):
        raise QValueError(f"The length of the specified longitude dimension names needs to be "
                          "equal to the number of netCDF data variables.\nLength of the specified longitude "
                          f"dimension names: {len(loncoord)}, number of netCDF data variables: {len(inputNCFile.data_vars)}.")
    lonval=[]    
    for lc,var in zip(loncoord,inputNCFile.data_vars):
        if lc not in inputNCFile[var].dims:
            raise QValueError(f"Specified longitude dimension '{lc}' not found in netCDF file's variable '{inputNCFile[var].name}'.")
        else:
            lonval.append(inputNCFile[var][lc].values.tolist())
    return lonval,loncoord

def check_level(inputNCFile,levcoord=None):
    if levcoord is None: #If user has not defined any longitude name
        levcoord = _get_dim_name(inputNCFile,dim_name='level')
    elif (len(levcoord)!=1) and (len(levcoord) != len(inputNCFile.data_vars)):
        raise QValueError(f"The length of the specified level dimension names needs to be "
                          "equal to the number of netCDF data variables.\nLength of the specified level "
                          f"dimension names: {len(levcoord)}, number of netCDF data variables: {len(inputNCFile.data_vars)}.")
    levval=[]
    for lc,var in zip(levcoord,inputNCFile.data_vars):
        if lc == 'None':
            levval.append([0])
        elif lc not in inputNCFile[var].dims:
            raise QValueError(f"Specified level dimension '{lc}' not found in netCDF file's variable '{inputNCFile[var].name}'.")
        else:
            levval.append(inputNCFile[var][lc].values.tolist())
    if len(levcoord) != len(inputNCFile.data_vars):
        levcoord = np.repeat(levcoord,len(inputNCFile.data_vars),axis=0).tolist()
        levval = np.repeat(levval,len(inputNCFile.data_vars),axis=0).tolist()
    return levval,levcoord

def check_time(inputNCFile,tcoord=None):
    if tcoord is None: #If user has not defined any longitude name
        for dim in ('time','t'):
            if dim in inputNCFile.dims:
                tcoord = dim
                break
        if tcoord is None:
            raise QValueError("No time dimension found in the netCDF file.\n"
                    "To specify the name of the time dimension in the netCDF "
                    "file use the '--time <name>' option.")
    elif tcoord not in inputNCFile.dims:
        raise QValueError(f"Specified time dimension '{tcoord}' not found in netCDF file.")
    return inputNCFile[tcoord].values.tolist(),tcoord
    