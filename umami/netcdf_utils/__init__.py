#!/usr/bin/env python

# Script created by Davide Marchegiani (davide.marchegiani@anu.edu.au) at ACCESS-NRI.

import sys

def get_dim_name(inputNCFile,dim_names,errmsg):
    for dim in dim_names:
        if dim in inputNCFile.dims:
            return dim
        else:
            sys.exit(errmsg)

