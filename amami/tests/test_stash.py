import pytest
from amami.um_utils import Stash  # This takes long to import!!
from hypothesis import given, strategies as st
# from unittest.mock import MagicMock, patch
# import re
# from amami.um_utils import (read_fieldsfile, get_grid_type,
#                             get_sealevel_rho, get_sealevel_theta, get_stash)
# import mule
# from iris.fileformats.pp import STASH as irisSTASH

REGEX_FOR_STRENCODED = Stash.REGEX_FOR_STRENCODED
REGEX_FOR_STRITEM = Stash.REGEX_FOR_STRITEM


@pytest.fixture
def stash_with_none() -> Stash:
    '''
    Create an example Stash instance without additional attributes, representing the following variable:
    long name: 'HALF OF (PEAK TO TROUGH HT OF OROG)'
    string code: 'm01s00i018'
    item code: 18
    name: ''
    units: ''
    standard_name: ''
    unique_name: ''

    reference: https://reference.metoffice.gov.uk/um/stash/_m01s00i018
    '''
    return Stash("m01s00i018")


@pytest.fixture
def stash_with_name() -> Stash:
    '''
    Create an example Stash instance with name attribute, representing the following variable:
    long name: 'OROGRAPHIC GRADIENT X COMPONENT'
    string code: 'm01s00i005'
    item code: 5
    name: 'orog_dx'
    units: ''
    standard_name: ''
    unique_name: ''

    reference: https://reference.metoffice.gov.uk/um/stash/_m01s00i005
    '''
    return Stash("m01s00i005")


@pytest.fixture
def stash_with_units() -> Stash:
    '''
    Create an example Stash instance with units attribute, representing the following variable:
    long name: 'BOUNDARY LAYER DEPTH AFTER TIMESTEP'
    string code: 'm01s00i025'
    item code: 25
    name: 'bldepth'
    units: 'm'
    standard_name: ''
    unique_name: ''

    reference: https://reference.metoffice.gov.uk/um/stash/_m01s00i025
    '''
    return Stash("m01s00i025")


@pytest.fixture
def stash_with_standard_name() -> Stash:
    '''
    Create an example Stash instance with standard_name attribute, representing the following variable:
    24: ["SURFACE TEMPERATURE AFTER TIMESTEP", "ts", "K", "surface_temperature", ""],
    long name: 'SURFACE TEMPERATURE AFTER TIMESTEP'
    string code: 'm01s00i024'
    item code: 24
    name: 'ts'
    units: 'K'
    standard_name: 'surface_temperature'
    unique_name: ''

    reference: https://reference.metoffice.gov.uk/um/stash/_m01s00i024
    '''
    return Stash("m01s00i024")


@pytest.fixture
def stash_with_all() -> Stash:
    '''
    Create an example Stash instance with all attributes, representing the following variable:
    long name: 'SPECIFIC HUMIDITY ON P LEV/T GRID'
    string code: 'm01s30i295'
    item code: 30295
    name: 'hus'
    units: '1'
    standard_name: 'specific_humidity'
    unique_name: 'hus_plev'
    '''
    return Stash("m01s30i295")


@given(st.from_regex(REGEX_FOR_STRENCODED, fullmatch=True))
def test_stash_from_string_encoded_nofail(string: str):
    Stash(string)


@given(st.from_regex(REGEX_FOR_STRITEM, fullmatch=True))
def test_stash_from_stringitem_nofail(string: str):
    Stash(string)


def test_stash_from_itemcode():
    stash = Stash(2003)
    assert stash.model == 1
    assert stash.section == 2
    assert stash.item == 3


def test_stash_from_stringitem():
    stash = Stash("2003")
    assert stash.model == 1
    assert stash.section == 2
    assert stash.item == 3


def test_stash_from_string_encoded():
    stash = Stash("m01s12i323")
    assert stash.model == 1
    assert stash.section == 12
    assert stash.item == 323

# def test_stash_string():
#     assert stash_without_params.string == "m01s01i002"

# # self.string = self._to_string()
# #         self.itemcode = self._to_itemcode()
# #         self.long_name = ""
# #         self.name = ""
# #         self.units = ""
# #         self.standard_name = ""
# #         self.unique_name = ""
# #         self._get_names()


# def test_stash_from_itemcode():
#     stash = Stash(2003)
#     assert stash.model == 1
#     assert stash.section == 2
#     assert stash.item == 3


# def test_stash_from_irisSTASH():
#     mock_iris_stash = MagicMock(spec=irisSTASH)
#     mock_iris_stash.model = 1
#     mock_iris_stash.section = 2
#     mock_iris_stash.item = 3
#     stash = Stash(mock_iris_stash)
#     assert stash.model == 1
#     assert stash.section == 2
#     assert stash.item == 3


# @pytest.mark.parametrize("code,model,section,item", [
#     ("m01s02i003", 1, 2, 3),
#     (2003, 1, 2, 3),
#     (irisSTASH(model=1, section=2, item=3), 1, 2, 3)
# ])
# def test_stash_initialization(code, model, section, item):
#     stash = Stash(code)
#     assert stash.model == model
#     assert stash.section == section
#     assert stash.item == item


# def test_stash_repr_str():
#     stash = Stash("m01s02i003")
#     expected_repr = "STASH m01s02i003 ()"
#     assert repr(stash) == expected_repr
#     assert str(stash) == expected_repr


# def test_stash_equality():
#     stash1 = Stash("m01s02i003")
#     stash2 = Stash(2003)
#     assert stash1 == stash2
#     assert stash1 != Stash("m01s02i004")


# @given(st.integers(min_value=0, max_value=54999))
# def test_stash_itemcode_hypothesis(itemcode):
#     stash = Stash(itemcode)
#     assert stash.itemcode == stash._to_itemcode()


# @given(st.text(min_size=9, max_size=10))
# def test_stash_string_hypothesis(strcode):
#     if re.match(r"^(m\d{2})?s\d{2}i\d{3}$", strcode):
#         stash = Stash(strcode)
#         assert stash.string == stash._to_string()
