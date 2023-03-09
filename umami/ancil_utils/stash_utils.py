# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

# Script created by Davide Marchegiani (davide.marchegiani@anu.edu.au) at ACCESS-NRI.

# /g/data3/hh5/public/apps/miniconda3/envs/analysis3-22.07/lib/python3.9/site-packages/mule/validators.py

from umami.quieterrors import QValueError
import re
def get_stash_name(itemcode):
    '''Get the name of the variable in the STASH code, based on the MetOffice STASH codes register
    (https://reference.metoffice.gov.uk/um/stash)
    '''
    def int2str(code):
        return f"m01s{code//1000:02d}i{code%1000:03d}"
    # Check the formatting of code
    if isinstance(itemcode,int):
        itemcode = int2code(itemcode)
    elif isinstance(itemcode,str) and not re.match(r"^m\d{2}s\d{2}i\d{3}$",itemcode):
        raise QValueError("Code string needs to be in the format 'mXXsXXiXXX', with X being "
                            "an integer between 0-9.")
    else:
        raise QValueError("Code needs to be either an integer or a string in the format "
                          "'mXXsXXiXXX', with X being an integer between 0-9")
    
    # from urllib.request import urlopen
    # htlm = urlopen("https://reference.metoffice.gov.uk/um/stash").read().decode("utf-8")
    with open("data/metoffice_stash_page",'r') as file:
        html = file.read()
    
    itemcode = "m01s02i204"
    a=re.findall(f"(?<=,)[^,]+(?=,{itemcode})",html)

# if len(a) == 0:
# elif len(a) > 1:
# else:y
