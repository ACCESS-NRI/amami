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
* Clean/simplify the `__main__` entrypoints
* Add `doc/docs` dir for more descriptive content/examples
* Add `.gitignore`
* Dead code removal (commented out & unused code)

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
  - `Cubes` already a datatype in `Iris`
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

### parsers

* Consider splitting examples into docs, more terse text for man page
* Refactor main parser
  - Replace classes with function calls? (simplify the code)
  - Fix formatting of multiline with `\n` chars
  - Merge modules into single module?
* Refactor `amami/parsers/core.py`, handle actions elsewhere?
* Fix triple quoting `amami/parsers/modify_parser.py`
  - Use justification in `textwrap` module if needed
  - Cleanup logic & parentheses in `callback_function()`
  - Refactor to use `argparse` API
  - Remove USAGE str, use `argparse` to generate help
  - Use non-optional args for input files
* Fix triple quoting `amami/parsers/um2nc_parser.py`
  - Use justification in `textwrap` module if needed
  - Cleanup logic & parentheses in `callback_function()`
  - Refactor to use `argparse` API
  - Remove USAGE str, use `argparse` to generate help

### stash_utils

* Refactor `amami/stash_utils/__init__.py` to `amami/stash.py`
* `atm_stashlist.py` is 4700 lines of constants, is this data in another python dependency?
* `Stash` class
  - Factor out constructor logic?
  - Why are the `_from_` functions marked as implementation as internal?
  - Refactor to `dataclass` with input/output functions?

### um_utils

* Move to `um_utils` module
* Delete `validation_tools.py`?
