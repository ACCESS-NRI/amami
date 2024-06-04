import pytest
from hypothesis import given, strategies as st
from unittest.mock import MagicMock, patch
import re
from amami.um_utils import (Stash, read_fieldsfile, get_grid_type,
                            get_sealevel_rho, get_sealevel_theta, get_stash)
import mule
from iris.fileformats.pp import STASH as irisSTASH


@pytest.fixture
def mock_umfile():
    mock_umfile = MagicMock(spec=mule.UMFile)
    mock_umfile.fixed_length_header.grid_staggering = 6
    mock_umfile.level_dependent_constants.zsea_at_rho = 1.0
    mock_umfile.level_dependent_constants.zsea_at_theta = 2.0
    mock_umfile.fields = [MagicMock(lbuser4=i) for i in range(10)]
    return mock_umfile


def test_read_fieldsfile():
    mock_umfile = MagicMock(spec=mule.UMFile)
    with patch('mule.load_umfile', return_value=mock_umfile):
        file = read_fieldsfile("fake_filename")
        assert file == mock_umfile


def test_get_grid_type(mock_umfile):
    assert get_grid_type(mock_umfile) == 'EG'


def test_get_sealevel_rho(mock_umfile):
    assert get_sealevel_rho(mock_umfile) == 1.0


def test_get_sealevel_theta(mock_umfile):
    assert get_sealevel_theta(mock_umfile) == 2.0


def test_get_stash(mock_umfile):
    stash_codes = get_stash(mock_umfile)
    assert stash_codes == list(range(10))


def test_get_stash_no_repeats(mock_umfile):
    mock_umfile.fields = [MagicMock(lbuser4=1), MagicMock(
        lbuser4=1), MagicMock(lbuser4=2)]
    stash_codes = get_stash(mock_umfile, repeat=False)
    assert stash_codes == [1, 2]
