# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

# Script created by Davide Marchegiani (davide.marchegiani@anu.edu.au) at ACCESS-NRI.

from umami.quieterrors import QValueError
import re
def get_stash_name(code):
    '''Get the name of the variable in the STASH code, based on the MetOffice STASH codes register
    (https://reference.metoffice.gov.uk/um/stash)
    '''
    def itemcode2strcode(code):
        return f"m01s{code//1000:02d}i{code%1000:03d}"
    # Check the formatting of code
    if isinstance(code,int):
        code = itemcode2strcode(code)
    elif isinstance(code,str) and not re.match(r"^m\d{2}s\d{2}i\d{3}$",code):
        raise QValueError("Code string needs to be in the format 'mXXsXXiXXX', with X being "
                            "an integer between 0-9.")
    else:
        raise QValueError("Code needs to be either an integer or a string in the format "
                          "'mXXsXXiXXX', with X being an integer between 0-9")
    
    # from urllib.request import urlopen
    # htlm = urlopen("https://reference.metoffice.gov.uk/um/stash").read().decode("utf-8")
    with open("data/metoffice_stash_page",'r') as file:
        html = file.read()
    
    code = "m01s02i204"
    a=re.findall(f"(?<=,)[^,]+(?=,{code})",html)

# if len(a) == 0:
# elif len(a) > 1:
# else:y
