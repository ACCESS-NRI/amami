# Project Review

Code/repo review April 2024. This is a list of items for preparing the `amami` for release.

## Global Changes

General changes applying to the entire project.

* Apply linter across code files
* Is licence header comment required in all Python modules?
  - Can it be deleted and referenced in a single file elsewhere? 
* Add requirements/versioning `requirements.txt`
* Why is the `.eggs` directory under version control?
  - Eggs have been deprecated
* Why is the `build` directory version controlled?

## Structural Changes

Suggested changes to simplify file & dir structure 

* Move `amami/core/modify.py` to `amami` dir
* Move `amami/core/um2nc.py` to `amami` dir
* Is `amami/data/metoffice_stash_page` required?
  - 7.5MB block of text/URLs (many duplicated URLs)
  - Tested several URLs, all failed on HTTP404
* Is any functionality duplicate & can be replaced by existing dependencies?
* Move `amami/loggers/__init__.py` to `amami/loggers.py`
* Consider removing `amami/misc_utils/__init__.py`
* Move `amami/netcdf_utils/__init__.py` to a base level module
  - Is the module needed?

## Module Changes

* Implement `cubes` as `dataclasses`?
* Add docstrings (at least for key modules)
* Remove unused imports
* Implement unit testing
  - How much architectural change is required?
* Replace magic numbers with constants

### loggers

* Compress/refactor logger code?
  - Use `functools.partial` to simplify substantially duplicated funcs
* Fix access to "internal" detail variables (refactor)

### netcdf_utils

* Split read & remove bands functionality
* Is any commented out code is required?
  - Does the netCDF API handle the funcs?
