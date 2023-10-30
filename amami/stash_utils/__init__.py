# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

"""
Module to define the Stash class to implement STASH-related functionalities 

Script created by Davide Marchegiani (davide.marchegiani@anu.edu.au) at ACCESS-NRI.
"""

# pylint: disable=logging-fstring-interpolation,import-outside-toplevel
from typing import Union
import re
from iris.fileformats.pp import STASH as irisSTASH
from amami.loggers import LOGGER

class Stash:
    """
    Class to implement STASH-related functionalities
    """
    def __init__(
        self,
        code:Union[str,int,irisSTASH],
    ):
        if isinstance(code,str):
            if not re.match(r"^(m\d{2})?s\d{2}i\d{3}$",code):
                LOGGER.error(
                    "STASH code string needs to be in the format '[m--]s--i---', with each "
                    "'-' being an integer between 0-9.\nThe part wrapped in squared brackets "
                    "('[]') is optional."
                )
            self.model,self.section,self.item = self._from_string(code)
        elif isinstance(code,int):
            if code > 54999 or code < 0:
                LOGGER.error(
                    f"Invalid STASH item code '{code}'. For item codes reference "
                    "please check the UM Documentation Paper C04 about 'Storage "
                    "Handling and Diagnostic System (STASH)' --> "
                    "https://code.metoffice.gov.uk/doc/um/latest/papers/umdp_C04.pdf"
                )
            self.model,self.section,self.item = self._from_itemcode(code)
        elif isinstance(code, irisSTASH):
            self.model,self.section,self.item = code.model,code.section,code.item
        self.string = self._to_string()
        self.itemcode = self._to_itemcode()
        self.long_name = ""
        self.name = ""
        self.units = ""
        self.standard_name = ""
        self.unique_name = ""
        self._get_names()

    def _from_string(
        self,
        strcode:str,
    ) -> tuple[int]:
        """Function to get the model, item and section from a STASH code string"""
        model = int(strcode[1:3]) if len(strcode)==10 else 1
        return model, int(strcode[-6:-4]), int(strcode[-3:])

    def _from_itemcode(
        self,
        itemcode:int,
    ) -> tuple[int]:
        """Function to get the model, item and section from a STASH item code"""
        itemcode = self.itemcode
        return 1, itemcode//1000, itemcode%1000

    def _to_string(self) -> str:
        """Function to return the STASH code string from model, section and item"""
        return f"m{self.model:02d}s{self.section:03d}i{self.item:03d}"

    def _to_itemcode(self) -> int:
        """Function to return the STASH item code from section and item"""
        return self.section*1000+self.item

    def _get_names(self):
        """
        Get STASH variable names based on the UM STASH Registry 
        (https://reference.metoffice.gov.uk/um/stash)
        """
        from amami.stash_utils.atm_stashlist import ATM_STASHLIST
        try:
            var = ATM_STASHLIST[self.itemcode]
        except KeyError:
            LOGGER.warning(
                f"Could not identify STASH variable from STASH item code '{self.itemcode}'."
            )
            var = ["UNKNOWN VARIABLE","", "", "", ""]
        self.long_name = var[0]
        self.name = var[1] if var[1] else self.string
        self.units = var[2]
        self.standard_name = var[3]
        self.unique_name = var[4] if var[4] else self.name

    # # from urllib.request import urlopen
    # # htlm = urlopen("https://reference.metoffice.gov.uk/um/stash").read().decode("utf-8")
    # with open("../data/metoffice_stash_page",'r') as file:
    #     html = file.read()
    # name=re.findall(f"(?<=,)[^,]+(?=,{code})",html)
    # if len(name) == 0:
    #     print("Warning: no item associated with the stash code provided.")
    #     name = code
    # return name
