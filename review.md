# Project Code Review

Code/repo review April 2024. This is a list of items for preparing the `amami` for release.

## Global Changes

General changes applying to the entire project.

* Apply linter across code files
  - Observation: `black` providing odd results in some cases (`ATM STASH`)
  - Use a configurable linter as some longer lines can't really br avoided?
* Is licence header comment required in all Python modules?
  - Can it be deleted and referenced in a single file elsewhere?
  - TODO: check the internal style guide (GH repo: `devdocs`)
* Add requirements/versioning `requirements.txt`?
  - Requirements currently in `setup.cfg`
  - TODO: check a packaging guide
* ~~Why is the `.eggs` directory under version control?~~
  - ~~Eggs have been deprecated~~
* ~~Why is the `build` directory version controlled?~~
* Clean/simplify the `__main__` entrypoints
  - TODO: Ben - what does this mean?
* Add `amami/docs` dir for more descriptive content/examples
  - Is a doc system like `sphinx` required? (likely)
  - Add docstrings (at least for key modules & functions (needed for `sphinx`)
* Expand `.gitignore`
  - Ben: check other branches
  - Remove `.DS_Store` & any other macturds from tracking
* Dead code removal (commented out & unused code)
* Configure repo for `coverage.py`
  - TODO: grab config from experimental branch
* Implement CI to include unit testing runs, coverage checks etc
  - Do GitHub actions cover our requirements?

## Structural Changes

Suggested changes to simplify file & dir structure 

* SKIP: Move `amami/commands/modify.py` to root `amami` dir (to simplify dir structure & imports)
* SKIP: Move `amami/commands/um2nc.py` to root `amami` dir
* ~~Is `amami/data/metoffice_stash_page` required?~~
  - ~~7.5MB block of text/URLs (many duplicated URLs)~~
  - ~~Tested several URLs, all failed on HTTP404~~
* Is any functionality duplicated & replaceable with existing dependencies?
  - Needs double check of some of the `um2nc` helper funcs
  - See the `iris.load()` & inbuilt cube filtering
  - TODO: what edge cases can be removed? (simplifies unit testing)
* Move `amami/loggers/__init__.py` to `amami/loggers.py`
* Consider removing `amami/misc_utils/__init__.py`
  - Is this now `helpers.py`?
* DEFER: Move `amami/netcdf_utils/__init__.py` to a root level `netcdf` module
  - Is the module needed? Will be part of a future review...

## Module Changes

General changes:

* ~~Implement `cubes` as `dataclasses`?~~
  - ~~`Cubes` already a datatype in `Iris`~~
* Remove unused imports
  - Add this as a CI/CD check/cleanup step?
  - TODO: what is the import cleaner tool? `ruff`?
* Implement unit testing
  - Requires architectural modification
  - Numerous functions require splitting/logic reordering etc to facilitate conversion to smaller, testable funcs
* Replace magic numbers with constants

### commands

* Refactor data processing modules (`um2nc.py` etc) main func(s) to take separate, documented input args
  - Expand args in `main()` command funcs (introduces an API for each command, which helps with clarity & testing)

### loggers

* DEFER Compress/refactor logger module code
  - SKIP? Use `functools.partial` to simplify substantially duplicated funcs?
  - Can default logging format/styling be overriden, removing the need for a custom logging class?
  - Try to remove the custom logger where custom methods are manually attached to the logger
  - See relevant logging refactoring issue

### netcdf_utils

* DEFER (file temp removed) Refactor: separate functionality to read & remove boundary coords
   Does the netCDF API handle the funcs?

### parsers

* FIXME: refactor multiple `ArgumentParser` declarations.
  - 4 parsers exist: `MainParser`, `SubCommandParser`, `help Parser`, `common Parser`
  - Simplify arg parsing overall
  - TODO: Extract args for clean calling of data processing commands
* Consider splitting examples into docs, more terse text for man page
* DEFER FROM HERE Refactor main parser
  - Replace classes with function calls? (simplify the code)
  - Fix formatting of multiline with `\n` chars
  - Merge modules into single module?
* Refactor `amami/parsers/core.py`, handle actions elsewhere?
* Fix triple quoting `amami/parsers/um2nc_parser.py`
  - TODO Confirm automatic dedentation in triple quoted strings
  - Cleanup formatting parentheses in `callback_function()`
  - Simplify the logic?
  - Refactor to use `argparse` API (defer: can argparse handle required customisation?)
  - Remove USAGE str, use `argparse` to generate help?

### stash_utils

* Refactor `amami/stash_utils/__init__.py` to `amami/stash.py` (package to module)
* `atm_stashlist.py` is 4700 lines of constants, is this data in another python dependency?
  - Not in a library, there's a canonical stash DB
* Refactor `Stash` class & `ATM_STASHLIST` to dict lookup (avoids `Stash` obj creation)
  - Implement `__getitem__`, `__aetitem__` to work with `str`, stash codes etc
  - Remove existing interface, use dict interface for standard python interoperability
  - TODO: find neat way to handle section/item code/int codes for the lookup (use annotation?)
  - `namedtuples` for `ATM_STASHLIST`
  - Move to `um_utils` module, as it's part of the unified model
* IDEA: subclass Iris `STASH` class:
  - Link to `ATM STASHLIST` to allow lookup from the custom class
  - https://github.com/SciTools/iris/blob/main/lib/iris/fileformats/pp.py
* IDEA: add `(section/code)` tuple keys for `ATM_STASHLIST` lookup?
  - con: doubles number of dict keys

### um_utils

* Convert from empty package to `amami/um_utils.py` module
* ~~Delete `validation_tools.py`?~~

## um2nc

* Use constraints arg in `iris.load()` to filter to required cubes first
  - This reduces repeated filtering further down in the function body
* Refactor logic in main (split function up for testing etc)
  - Split in pre & post processing funcs for each data library? (split `mule` & `iris` ops out to separate functions)
  - Refactor I/O to separate functions
* Refactor include/exclude functionality:
  - Return list of names to keep
  - Validation: ensure no common items between include/exclude
  - Simplify logic so default args are empty containers?
* Fix heavi/heavy (heaviside/heavyside) naming - is this a typo?
* Fix exception based control flow in `um2nc.cubewrite()`
  - Manually check for ancilliary file (other file types? make check explicit for code clarity)
  - Split modification & write steps into separate funcs
* Saving: can cubes & global metadata be modified, then `save()` relying on the file extension?
  - Can this get around I/O sprinkled throughout `main()`?
* Needs unit tests
