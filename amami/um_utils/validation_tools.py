# Copyright 2022 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

# Script created by Davide Marchegiani (davide.marchegiani@anu.edu.au) at ACCESS-NRI.

# /g/data3/hh5/public/apps/miniconda3/envs/analysis3-22.07/lib/python3.9/site-packages/mule/validators.py

# from mule.validators import ValidateError
# from amami.quieterrors import QFixError
# import sys

# def validate(ancilFile,fix=False,filename=None):
#     # Validate ancillary file.
#     try:
#         ancilFile.validate()
#     except ValidateError as e:
#         if filename is None:
#             text = ""
#         else:
#             text = f"for '{filename}' "
#         print(f"Validation failed {text}with the following error message:\n"+\
#                 "'{}'.".format('\n'.join(str(e).split('\n')[1:])))
#         if not fix:
#             sys.exit()
#         else:
#             print("Fixing validation error...")
#             ancilFile = _fix_error(e,ancilFile)
#             print("Validation error fixed!\n")
#     return ancilFile

# def _input(values,prompt):
#     output = input(prompt) 
#     while output not in [str(v) for v in values]:
#         output = input("Invalid value inserted. " + prompt)
#     return output
    
# def _fix_error(error,ancilFile):
#     '''
#     Function that fixes an ancilFile based on the UM Documentation Paper F03, and user inputs.
#     '''
#     errorString = '\n'.join(str(error).split('\n')[1:])
#     newAncilFile = ancilFile.copy(include_fields=True)
#     end_prompt = "\nFor better reference check the UM Documentation Paper F03 --> https://code.metoffice.gov.uk/doc/um/latest/papers/umdp_F03.pdf\n"
#     # Handle Error: 1
#     if errorString.startswith("Ancillary file contains header components other than the"):
#         newAncilFile.level_dependent_constants = None
#     # Handle Error: 2
#     elif errorString.startswith("Unsupported grid_staggering"):
#         values=(3,6)
#         grid_staggering = _input(values,f"Please choose a grid staggering value in {values}."+end_prompt)
#         newAncilFile.fixed_length_header.grid_staggering = grid_staggering
#     # Handle Error: 3
#     elif "Cannot validate field due to incompatible grid type:" in errorString:
#         values = (0,1,2,3,4,101,102,103,104) 
#         grid_type =_input(values,f"Please choose a grid type value in {values}."+end_prompt)
#         newAncilFile.fixed_length_header.horiz_grid_type = int(grid_type)
#         for f in newAncilFile.fields: f.lbhem = int(grid_type)%100
#     else:
#         raise QFixError("The validation error above could not be fixed or is currently not supported.")
#     return newAncilFile




