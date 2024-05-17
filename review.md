# Project Code Review

Code/repo review April 2024. This is a list of items for preparing the `amami` for release.

## Global Changes

General changes applying to the entire project.

* Apply linter across code files
  - Observation: `black` providing odd results in some cases (`ATM STASH`)
  - Use a configurable linter as some longer lines can't really br avoided?
* Is licence header comment required in all Python modules?
  - Can it be deleted and referenced in a single file elsewhere? 
* Add requirements/versioning `requirements.txt`?
  - Requirements currently in `setup.cfg`
* ~~Why is the `.eggs` directory under version control?~~
  - ~~Eggs have been deprecated~~
* ~~Why is the `build` directory version controlled?~~
* Clean/simplify the `__main__` entrypoints
* Add `amami/docs` dir for more descriptive content/examples
  - Is a doc system like `sphinx` required?
* Expand `.gitignore`
* Remove `.DS_Store` & any other macturds from tracking
* Dead code removal (commented out & unused code)
* Configure repo for `coverage.py`
* Implement CI unit testing, coverage checks etc

## Structural Changes

Suggested changes to simplify file & dir structure 

* Move `amami/core/modify.py` to root `amami` dir (to simplify dir structure & imports)
* Move `amami/core/um2nc.py` to root `amami` dir
* ~~Is `amami/data/metoffice_stash_page` required?~~
  - ~~7.5MB block of text/URLs (many duplicated URLs)~~
  - ~~Tested several URLs, all failed on HTTP404~~
* Is any functionality duplicated & replaceable with existing dependencies?
* Move `amami/loggers/__init__.py` to `amami/loggers.py`
* Consider removing `amami/misc_utils/__init__.py`
* Move `amami/netcdf_utils/__init__.py` to a root level `netcdf` module
  - Is the module needed?

## Module Changes

General changes:

* ~~Implement `cubes` as `dataclasses`?~~
  - ~~`Cubes` already a datatype in `Iris`~~
* Add docstrings (at least for key modules)
* Remove unused imports
  - Add this as a CI/CD step?
  - TODO: what is the import cleaner tool?
* Implement unit testing
  - Requires architectural modification
  - Numerous functions require splitting/logic reordering etc to facilitate conversion to smaller, testable funcs
* Replace magic numbers with constants

### core

* Refactor data processing modules (`um2nc.py` etc) main func(s) to take separate input args
  - Code currently coupled to arg parsers to create inputs & pass a single args obj (splits the um2nc API away from the module, which affects testing)
  - Separate args in main increases readability, API clarity & docs & has testing benefits)

### loggers

* Compress/refactor logger module code
  - Use `functools.partial` to simplify substantially duplicated funcs?
  - Can default logging format/styling be overriden, removing the need for a custom logging class?
  - Try to remove the custom logger where custom methods are manually attached to the logger
  - See relevant logging refactoring issue

### netcdf_utils

* Refactor: separate functionality to read & remove bands
* Is any commented out code is required?
  - Does the netCDF API handle the funcs?

### parsers

* FIXME: refactor multiple `ArgumentParser` declarations.
  - 4 parsers exist: `MainParser`, `SubCommandParser`, `help Parser`, `common Parser`
  - Simplify arg parsing overall
  - Extract args for clean calling of data processing commands
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

* Refactor `amami/stash_utils/__init__.py` to `amami/stash.py` (package to simple module)
* `atm_stashlist.py` is 4700 lines of constants, is this data in another python dependency?
* Refactor `Stash` class & `ATM_STASHLIST` to dict lookup (avoids `Stash` obj creation)
  - Implement `__getitem__`, `__aetitem__` to work with `str`, stash codes etc
  - Remove existing interface, use dict interface for standard python interoperability
  - Move to `um_utils` module, as it's part of the unified model

### um_utils

* Move to `um_utils` module
* Delete `validation_tools.py`?

## um2nc

* Use constraints arg in opener to filter/open required cubes first (saves filtering)
* Refactor logic in main (split function up)
  - Split in pre & post processing funcs for each data library?
  - Refactor I/O to separate functions
* Factor include/exclude functionality:
  - Return list of names to keep
  - Validation: ensure no common items between include/exclude
  - Simplify logic so default args are empty containers
* Fix heavi/heavy naming - is this a typo?
* Fix exception based control flow in `um2nc.cubewrite()`
  - Manually check for ancilliary file
  - Split modification & write steps into separate funcs
* Saving: can cubes & global metadata be modified, then `save()` relying on the file extension?
  - Can this get around I/O sprinkled throughout `main()`?
