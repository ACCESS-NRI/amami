# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

"""
Script created by Davide Marchegiani (davide.marchegiani@anu.edu.au) at ACCESS-NRI.

Utility module for UM fieldsfiles and STASH-related functionalities
"""

import re
import mule
from typing import Union, List
from amami.loggers import LOGGER
from iris.fileformats.pp import STASH as irisSTASH
from amami._atm_stashlist import ATM_STASHLIST

IMDI = -32768  # (-2.0**15)
RMDI = -1073741824.0  # (-2.0**30)


class UMError(Exception):
    """Base Exception for Unified Model related errors"""
    pass


class Stash:
    """
    Class to implement STASH-related functionalities
    """

    __slots__ = [
        "model",
        "section",
        "item",
        "string",
        "itemcode",
        "long_name",
        "name",
        "units",
        "standard_name",
        "unique_name",
    ]

    def __init__(self, code: Union[str, int, irisSTASH]):
        if isinstance(code, str):
            if re.match(r"^(m\d{2})?s\d{2}i\d{3}$", code):
                self.model, self.section, self.item = self._from_string(code)
            elif re.match(r"^\d{1,5}$", code):
                code = int(code)
                if code > 54999 or code < 0:
                    # TODO: refactor to single message
                    msg = (f"Invalid STASH item code '{code}'. For item codes reference please "
                           "check the UM Documentation Paper C04 about 'Storage Handling and "
                           "Diagnostic System (STASH)' --> "
                           "https://code.metoffice.gov.uk/doc/um/latest/papers/umdp_C04.pdf")
                    raise UMError(msg)
                self.model, self.section, self.item = self._from_itemcode(code)
            else:
                msg = ("STASH code needs to be either an integer between 0 and 54999, or a string "
                       "in the format '[m--]s--i---', with each '-' being an integer between 0-9.\n"
                       "The part wrapped in squared brackets ('[]') is optional.")
                raise UMError(msg)
        elif isinstance(code, int):
            if code > 54999 or code < 0:
                msg = (f"Invalid STASH item code '{code}'. For item codes reference please "
                       "check the UM Documentation Paper C04 about 'Storage Handling and "
                       "Diagnostic System (STASH)' --> "
                       "https://code.metoffice.gov.uk/doc/um/latest/papers/umdp_C04.pdf")
                raise UMError(msg)
            self.model, self.section, self.item = self._from_itemcode(code)
        elif isinstance(code, irisSTASH):
            self.model, self.section, self.item = code.model, code.section, code.item

        self.string = self._to_string()
        self.itemcode = self._to_itemcode()
        self.long_name = ""
        self.name = ""
        self.units = ""
        self.standard_name = ""
        self.unique_name = ""
        self._get_names()

    def __repr__(self):
        """
        Representation of Stash class.
        """
        return f"STASH {self.string} ({self.long_name})"
    
    def __str__(self):
        """
        Representation of Stash class when printed out.
        """
        return f"STASH {self.string} ({self.long_name})"
    
    def __eq__(self, other):
        """
        Set criteria to check equality for Stash class instances.
        """
        if isinstance(other, Stash):
            return other.itemcode == self.itemcode
        elif isinstance(other, str):
            return self.string == other or self.long_name == other
        elif isinstance(other, int):
            return self.itemcode == other
        elif isinstance(other, irisSTASH):
            return self.model == other.model and self.section == other.section and self.item == other.item
        else:
            return False
    
    def __ne__(self, other):
        return not self.__eq__(other)

    def _from_string(self, strcode: str) -> tuple[int]:
        """Function to get the model, item and section from a STASH code string"""
        model = int(strcode[1:3]) if len(strcode) == 10 else 1
        return model, int(strcode[-6:-4]), int(strcode[-3:])

    def _from_itemcode(self, itemcode: int) -> tuple[int]:
        """Function to get the model, item and section from a STASH item code"""
        return 1, itemcode // 1000, itemcode % 1000

    def _to_string(self) -> str:
        """Function to return the STASH code string from model, section and item"""
        return f"m{self.model:02d}s{self.section:02d}i{self.item:03d}"

    def _to_itemcode(self) -> int:
        """Function to return the STASH item code from section and item"""
        return self.section*1000+self.item

    def _get_names(self):
        """
        Get STASH variable names based on the UM STASH Registry 
        (https://reference.metoffice.gov.uk/um/stash)
        """
        try:
            var = ATM_STASHLIST[self.itemcode]
        except KeyError:
            LOGGER.warning(
                "Could not identify STASH variable from STASH item code %s.",
                self.itemcode,
            )
            var = ["UNKNOWN VARIABLE", "", "", "", ""]
        self.long_name = var[0]
        self.name = var[1] if var[1] else self.string
        self.units = var[2]
        self.standard_name = var[3]
        self.unique_name = var[4] if var[4] else self.name


def read_fieldsfile(um_filename: str, check_ancil: bool = False) -> type[mule.UMFile]:
    """Read UM fieldsfile with mule, and optionally check if type is AncilFile"""

    try:
        ufile = mule.load_umfile(um_filename)
        ufile.remove_empty_lookups()
    except ValueError:
        raise UMError(f"'{um_filename.resolve()}' does not appear to be a UM file.")

    if check_ancil and (not isinstance(ufile, mule.ancil.AncilFile)):
        raise UMError(f"'{um_filename}' does not appear to be a UM ancillary file.")

    return ufile


def get_grid_type(um_file: type[mule.UMFile]) -> str:
    """Get UM grid type from mule UMFile"""
    gs = um_file.fixed_length_header.grid_staggering
    if gs == 6:
        return "EG"  # End Game
    elif gs == 3:
        return "ND"  # New Dynamics

    raise UMError(f"Unrecognised grid staggering in UM Fieldsfile header: '{gs}' not supported.")


def get_sealevel_rho(um_file: type[mule.UMFile]) -> float:
    """Get UM sea level on rho levels from mule UMFile"""
    try:
        return um_file.level_dependent_constants.zsea_at_rho
    except AttributeError:
        return 0.


def get_sealevel_theta(um_file: type[mule.UMFile]) -> float:
    """Get UM sea level on thetha levels from mule UMFile"""
    try:
        return um_file.level_dependent_constants.zsea_at_theta
    except AttributeError:
        return 0.


def get_stash(um_file: type[mule.UMFile], repeat: bool = True) -> List:
    """
    Get ordered list of stash codes in mule UMFile
    with (repeat = True) or without (repeat = False) repetitions.
    """
    stash_codes = [f.lbuser4 for f in um_file.fields]
    if not repeat:
        return list(dict.fromkeys(stash_codes))
    return stash_codes
