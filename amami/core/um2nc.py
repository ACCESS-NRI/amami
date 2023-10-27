#!/usr/bin/env python3

# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

# pylint: disable=logging-fstring-interpolation,import-outside-toplevel,broad-exception-caught
"""
Original script (/g/data/access/projects/access/apps/pythonlib/um2netcdf4/2.1/um2netcdf4.py) 
created by Martin Dix.

Modified by Davide Marchegiani at ACCESS-NRI - davide.marchegiani@anu.edu.au

Convert a UM fieldsfile to netCDF
"""
import datetime
import numpy as np
import cf_units
import cftime
import netCDF4
import amami
from amami.stash_utils import Stash
import amami.um_utils as umutils
from amami.loggers import LOGGER
from amami import io

def get_nc_format(format_arg:str) -> str:
    """Convert format numbers to format strings"""
    nc_formats = {
        1:'NETCDF4',
        2:'NETCDF4_CLASSIC',
        3:'NETCDF3_CLASSIC',
        4: 'NETCDF3_64BIT',
    }
    try:
        return nc_formats[int(format_arg)]
    except ValueError:
        return format_arg

def add_global_attrs(
    infile,
    fid,
    nohist
) -> None:
    """Add global attributes to converted NetCDF file"""
    if not nohist:
        date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        history = f"File {infile} converted with 'amami um2nc' v{amami.__version__} "\
            f"on {date}"
        fid.update_global_attributes({'history':history})
    fid.update_global_attributes({'Conventions':'CF-1.6'})

def get_heaviside_uv(cubes):
    """Get heaviside_uv field if UM file has it, otherwise return None"""
    for c in cubes:
        if Stash(c.attributes['STASH']).itemcode == 30301:
            return c
    return None

def get_heaviside_t(cubes):
    """Get heaviside_t field if UM file has it, otherwise return None"""
    for c in cubes:
        if Stash(c.attributes['STASH']).itemcode == 30304:
            return c
    return None

def apply_mask_to_pressure_level_field(
    cube,
    stash,
    heaviside_uv,
    heaviside_t,
    hcrit,
):
    """
    Check whether there are any pressure level fields that should be masked
    using heaviside function and mask them.
    """
    itemcode = stash.itemcode
    # Heaviside_uv
    if ((30201 <= itemcode <= 30288)
    or
    (30302 <= itemcode <= 30303)):
        if heaviside_uv:
            apply_mask(cube, heaviside_uv, hcrit)
        else:
            LOGGER.warning(
            "Heaviside_uv field needed for masking pressure level data "
            f"is not present. The field 'ITEMCODE:{itemcode} -- "
            f"{stash.long_name}' will be skipped.\n"
            "If you still want convert this field without masking, "
            "use the '--nomask' option."
            )
            return False
    # Heaviside_t
    elif 30293 <= itemcode <= 30298:
        if heaviside_t:
            apply_mask(cube, heaviside_t, hcrit)
        else:
            LOGGER.warning(
            "Heaviside_t field needed for masking pressure level data "
            f"is not present. The field 'ITEMCODE:{itemcode} -- "
            f"{stash.long_name}' will be skipped.\n"
            "If you still want convert this field without masking, "
            "use the '--nomask' option."
            )
            return False
    return True

def main(args):
    """Main function for `um2nc` subcommand"""
    LOGGER.debug(f"{args=}")
    infile = io.get_abspath(getattr(args,'infile'))
    LOGGER.debug(f"{infile=}")
    # Use mule to get the model levels to help with dimension naming
    LOGGER.info(f"Reading UM file {infile} ...")
    ff = umutils.read_fieldsfile(infile, check_ancil=False)
    import iris
    import iris.coords
    try:
        cubes = iris.load(infile)
    except iris.exceptions.CannotAddError:
        LOGGER.error(
            "UM file can not be processed. UM files with time series currently not supported.\n"
            "Please convert using convsh (https://ncas-cms.github.io/xconv-doc/html/example1.html)."
        )
    # Get order of fields (from stash codes)
    stash_order = list(dict.fromkeys([f.lbuser4 for f in ff.fields]))
    LOGGER.debug(f"{stash_order=}")
    # Order the cubelist based on input order
    cubes.sort(key = lambda c:
               stash_order.index(c.attributes['STASH'].section*1000 + c.attributes['STASH'].item))
    # Get heaviside fields for pressure level masking    
    if not args.nomask:
        heaviside_uv = get_heaviside_uv(cubes)
        heaviside_t = get_heaviside_t(cubes)

    outfile = io.get_abspath(getattr(args,'outfile'),check=False)
    
    grid_type = umutils.get_grid_type(ff)
    z_rho = umutils.get_sealevel_rho(ff)
    z_theta = umutils.get_sealevel_theta(ff)

    try:
        with iris.fileformats.netcdf.Saver(outfile, get_nc_format(args.format)) as sman:
            # Add global attributes
            add_global_attrs(infile, sman, args.nohist)

            for c in cubes:
                stash = Stash(c.attributes['STASH'])
                itemcode = stash.itemcode
                if args.include_list and itemcode not in args.include_list:
                    continue
                if args.exclude_list and itemcode in args.exclude_list:
                    continue
                if args.simple:
                    c.var_name = 'fld_s%2.2di%3.3d' % (stash.section, stash.item)
                elif stash.uniquename:
                    c.var_name = stash.uniquename
                # Could there be cases with both max and min?
                if c.var_name:
                    if any([m.method == 'maximum' for m in c.cell_methods]):
                        c.var_name += "_max"
                    if any([m.method == 'minimum' for m in c.cell_methods]):
                        c.var_name += "_min"
                # The iris name mapping seems wrong for these - perhaps assuming rotated grids?
                if c.standard_name == 'x_wind':
                    c.standard_name = 'eastward_wind'
                if c.standard_name == 'y_wind':
                    c.standard_name = 'northward_wind'
                if c.standard_name and stash.standard_name:
                    if c.standard_name != stash.standard_name:
                        LOGGER.warning(f"Standard name mismatch {stash.section} {stash.item} {c.standard_name} {stash.standard_name}\n")
                        c.standard_name = stash.standard_name
                if str(c.units) != stash.units:
                    LOGGER.warning(f"Units mismatch {stash.section} {stash.item} {c.units} {stash.units}\n")
                    c.units = stash.units
                # If there's no standard_name or long_name from iris use one from STASH
                if not c.standard_name:
                    if stash.standard_name:
                        c.standard_name = stash.standard_name
                if not c.long_name:
                    if stash.long_name:
                        c.long_name = stash.long_name

                # Interval in cell methods isn't reliable so better to remove it.
                c.cell_methods = fix_cell_methods(c.cell_methods)
                try:
                    fix_latlon_coord(c, grid_type)
                except iris.exceptions.CoordinateNotFoundError:
                    if args.verbose:
                        print(c)
                    raise SystemExit("File can not be processed. UM files with time series currently not supported.\n"
                                     "Please convert using convsh (https://ncas-cms.github.io/xconv-doc/html/example1.html).")
                fix_level_coord(c, z_rho, z_theta)
                
                if not args.nomask:
                    if not apply_mask_to_pressure_level_field(
                        c,
                        stash,
                        heaviside_uv,
                        heaviside_t,
                        args.hcrit
                    ):
                        continue
                
                LOGGER.info(c.name(), itemcode)
                cubewrite(c, sman, args.compression, args.use64bit, args.verbose)
    except Exception as e: #If there is an error, remove the netCDF file created
        outfile.unlink(missing_ok=True)
        LOGGER.error(e)

def apply_mask(c, heaviside, hcrit):
    # Function must handle case where the cube is defined on only a subset of the levels of the heaviside function
    # print("Apply mask", c.shape, heaviside.shape)
    if c.shape == heaviside.shape:
        # If the shapes match it's simple
        # Temporarily turn off warnings from 0/0
        with np.errstate(divide='ignore',invalid='ignore'):
            c.data = np.ma.masked_array(c.data/heaviside.data, heaviside.data <= hcrit).astype(np.float32)
    else:
        # Are the levels of c a subset of the levels of the heaviside variable?
        c_p = c.coord('pressure')
        h_p = heaviside.coord('pressure')
        # print('Levels for masking', c_p.points, h_p.points)
        if set(c_p.points).issubset(h_p.points):
            # Match is possible
            constraint = iris.Constraint(pressure=c_p.points)
            h_tmp = heaviside.extract(constraint)
            # Double check they're actually the same after extraction
            if not np.all(c_p.points == h_tmp.coord('pressure').points):
                raise QValueError('Unexpected mismatch in levels of extracted heaviside function')
            with np.errstate(divide='ignore',invalid='ignore'):
                c.data = np.ma.masked_array(c.data/h_tmp.data, h_tmp.data <= hcrit).astype(np.float32)
        else:
            raise QValueError('Unable to match levels of heaviside function to variable %s' % c.name())

# def convert_proleptic(time):
#     """Convert units from hours to days and shift origin from 1970 to 0001"""
#     newunits = cf_units.Unit("days since 0001-01-01 00:00", calendar='proleptic_gregorian')
#     # Need a copy because can't assign to time.points[i]
#     tvals = np.array(time.points)
#     if time.bounds is not None:
#         tbnds = np.array(time.bounds)
#         has_bnds = True
#     else:
#         has_bnds = False
#     for i in range(len(time.points)):
#         date = time.units.num2date(tvals[i])
#         newdate = cftime.DatetimeProlepticGregorian(date.year, date.month, date.day, date.hour, date.minute, date.second)
#         tvals[i] = newunits.date2num(newdate)
#         if has_bnds: # Fields with instantaneous data don't have bounds
#             for j in range(2):
#                 date = time.units.num2date(tbnds[i][j])
#                 newdate = cftime.DatetimeProlepticGregorian(date.year, date.month, date.day, date.hour, date.minute, date.second)
#                 tbnds[i][j] = newunits.date2num(newdate)
#     time.points = tvals
#     if has_bnds:
#         time.bounds = tbnds
#     time.units = newunits

# def fix_latlon_coord(cube, grid_type):
#     def _add_coord_bounds(coord):
#         if len(coord.points) > 1:
#             if not coord.has_bounds():
#                 coord.guess_bounds()
#         else:
#             # For length 1, assume it's global. guess_bounds doesn't work in this case
#             if coord.name() == 'latitude':
#                 if not coord.has_bounds():
#                     coord.bounds = np.array([[-90.,90.]])
#             elif coord.name() == 'longitude':
#                 if not coord.has_bounds():
#                     coord.bounds = np.array([[0.,360.]])

#     lat = cube.coord('latitude')
#     # Force to double for consistency with CMOR
#     lat.points = lat.points.astype(np.float64)
#     _add_coord_bounds(lat)
#     lon = cube.coord('longitude')
#     lon.points = lon.points.astype(np.float64)
#     _add_coord_bounds(lon)

#     lat = cube.coord('latitude')
#     if len(lat.points) == 180:
#         lat.var_name = 'lat_river'
#     elif (lat.points[0] == -90 and grid_type == 'EG') or \
#          (np.allclose(-90.+np.abs(0.5*(lat.points[1]-lat.points[0])), lat.points[0]) and grid_type == 'ND'):
#         lat.var_name = 'lat_v'
#     else:
#         lat.var_name = 'lat'

#     lon = cube.coord('longitude')
#     if len(lon.points) == 360:
#         lon.var_name = 'lon_river'
#     elif (lon.points[0] == 0 and grid_type == 'EG') or \
#          (np.allclose(np.abs(0.5*(lon.points[1]-lon.points[0])), lon.points[0]) and grid_type == 'ND'):
#         lon.var_name = 'lon_u'
#     else:
#         lon.var_name = 'lon'

# def fix_level_coord(cube, z_rho, z_theta):
#     # Rename model_level_number coordinates to better distinguish rho and theta levels
#     try:
#         c_lev = cube.coord('model_level_number')
#         c_height = cube.coord('level_height')
#         c_sigma = cube.coord('sigma')
#     except iris.exceptions.CoordinateNotFoundError:
#         c_lev = None
#     if c_lev:
#         d_rho = abs(c_height.points[0]-z_rho)
#         if d_rho.min() < 1e-6:
#             c_lev.var_name = 'model_rho_level_number'
#             c_height.var_name = 'rho_level_height'
#             c_sigma.var_name = 'sigma_rho'
#         else:
#             d_theta = abs(c_height.points[0]-z_theta)
#             if d_theta.min() < 1e-6:
#                 c_lev.var_name = 'model_theta_level_number'
#                 c_height.var_name = 'theta_level_height'
#                 c_sigma.var_name = 'sigma_theta'


# def cubewrite(cube, sman, compression, use64bit, verbose):
#     try:
#         plevs = cube.coord('pressure')
#         plevs.attributes['positive'] = 'down'
#         plevs.convert_units('Pa')
#         # Otherwise they're off by 1e-10 which looks odd in ncdump
#         plevs.points = np.round(plevs.points,5)
#         if plevs.points[0] < plevs.points[-1]:
#             # Flip to get pressure decreasing as in CMIP6 standard
#             cube = iris.util.reverse(cube, 'pressure')
#     except iris.exceptions.CoordinateNotFoundError:
#         pass
#     if not use64bit:
#         if cube.data.dtype == 'float64':
#             cube.data = cube.data.astype(np.float32)
#         elif cube.data.dtype == 'int64':
#             cube.data = cube.data.astype(np.int32)

#     # Set the missing_value attribute. Use an array to force the type to match
#     # the data type
#     if cube.data.dtype.kind == 'f':
#         fill_value = 1.e20
#     else:
#         # Use netCDF defaults
#         fill_value = netCDF4.default_fillvals['%s%1d' % (cube.data.dtype.kind, cube.data.dtype.itemsize)]

#     cube.attributes['missing_value'] = np.array([fill_value], cube.data.dtype)

#     # If reference date is before 1600 use proleptic gregorian
#     # calendar and change units from hours to days
#     try:
#         reftime = cube.coord('forecast_reference_time')
#         time = cube.coord('time')
#         refdate = reftime.units.num2date(reftime.points[0])
#         assert time.units.origin == 'hours since 1970-01-01 00:00:00'
#         if time.units.calendar == 'proleptic_gregorian' and refdate.year < 1600:
#             convert_proleptic(time)
#         else:
#             if time.units.calendar == 'gregorian':
#                 new_calendar = 'proleptic_gregorian'
#             else:
#                 new_calendar = time.units.calendar
#             time.units = cf_units.Unit("days since 1970-01-01 00:00", calendar=new_calendar)
#             time.points = time.points/24.
#             if time.bounds is not None:
#                 time.bounds = time.bounds/24.
#         cube.remove_coord('forecast_period')
#         cube.remove_coord('forecast_reference_time')
#     except iris.exceptions.CoordinateNotFoundError:
#         # Dump files don't have forecast_reference_time
#         pass

#     # Check whether any of the coordinates is a pseudo-dimension
#     # with integer values and if so reset to int32 to prevent
#     # problems with possible later conversion to netCDF3
#     for coord in cube.coords():
#         if coord.points.dtype == np.int64:
#             coord.points = coord.points.astype(np.int32)

#     try:
#         # If time is a dimension but not a coordinate dimension, coord_dims('time') returns an empty tuple
#         if tdim := cube.coord_dims('time'):
#             # For fields with a pseudo-level, time may not be the first dimension
#             if tdim != (0,):
#                 tdim = tdim[0]
#                 neworder = list(range(cube.ndim))
#                 neworder.remove(tdim)
#                 neworder.insert(0,tdim)
#                 if verbose > 1:
#                     print("Incorrect dimension order", cube)
#                     print("Transpose to", neworder)
#                 cube.transpose(neworder)
#             sman.write(cube, zlib=True, complevel=compression, unlimited_dimensions=['time'], fill_value=fill_value)
#         else:
#             tmp = iris.util.new_axis(cube,cube.coord('time'))
#             sman.write(tmp, zlib=True, complevel=compression, unlimited_dimensions=['time'], fill_value=fill_value)
#     except iris.exceptions.CoordinateNotFoundError:
#         # No time dimension (probably ancillary file)
#         sman.write(cube, zlib=True, complevel=compression, fill_value=fill_value)

# def fix_cell_methods(mtuple):
#     # Input is tuple of cell methods
#     newm = []
#     for m in mtuple:
#         newi = []
#         for i in m.intervals:
#             # Skip the misleading hour intervals
#             if i.find('hour') == -1:
#                 newi.append(i)
#         n = iriscoords.CellMethod(m.method, m.coord_names, tuple(newi), m.comments)
#         newm.append(n)
#     return tuple(newm)