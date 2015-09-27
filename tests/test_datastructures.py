# -*- coding: UTF-8 -*-

from mock import patch
import pytest

from mcm.datastructures import CmdPathRow, make_cmdpath


@patch('mcm.datastructures.MENU_PATHS')
class Test_CmdPath:

    @pytest.mark.parametrize("path",("/ip/address/", "ip/address", "/ip/address"))
    def test_absolute_attribute(self, paths_mock, path):
        cmd_path = make_cmdpath(path, strategy=None)
        assert cmd_path.absolute == '/ip/address'

    def test_strategy_attribute_is_the_same_as_passed_in_function_call(self, paths_mock):
        cmd_path = make_cmdpath('/ip/address', strategy='exact')
        assert cmd_path.strategy == 'exact'

    def test_calls_getitem_on_paths_data_structure(self, paths_mock):
        make_cmdpath('/ip/address', strategy='exact')
        paths_mock.__getitem__.assert_called_once_with('/ip/address')

    def test_calling_getitem_on_paths_data_structure_riases_KeyError_when_path_is_missing(self, paths_mock):
        paths_mock.__getitem__.side_effect = KeyError
        with pytest.raises(KeyError):
            make_cmdpath('/ip/address', 'exact')


@pytest.mark.parametrize("data,expected", (
    ( {'enabled':True}, 'enabled=yes' ),
    ( {'enabled':False}, 'enabled=no' ),
    ( {'servers':None}, 'servers=""' ),
    ( {'servers':''}, 'servers=""' ),
    ))
def test_CmdPathRow_str(data, expected):
    assert str(CmdPathRow(data)) == expected


def test_sub_returns_CmdPathRow_instance():
    assert isinstance((CmdPathRow() - CmdPathRow()), CmdPathRow )


@pytest.mark.parametrize("wanted,present,expected",(
    (CmdPathRow(interface='ether1', disabled=False), CmdPathRow(interface='ether1', disabled=False), CmdPathRow()),
    (CmdPathRow(interface='ether2', disabled=False), CmdPathRow(interface='ether1', disabled=False), CmdPathRow(interface='ether2')),
    (CmdPathRow(interface='ether1', disabled=False), CmdPathRow(interface='ether2', disabled=False), CmdPathRow(interface='ether1')),
    ))
def test_difference(wanted,present,expected):
    assert (wanted - present) == expected


@pytest.mark.parametrize("expected,keys,row1,row2",(
    (True, ('interface',), CmdPathRow(interface='ether1', disabled=False), CmdPathRow(interface='ether1', disabled=False)),
    (True, ('interface','disabled'), CmdPathRow(interface='ether1', disabled=False), CmdPathRow(interface='ether1', disabled=False)),
    (False, ('interface',), CmdPathRow(interface='ether2', disabled=False), CmdPathRow(interface='ether1', disabled=False)),
    (False, ('interface','disabled'), CmdPathRow(interface='ether2', disabled=False), CmdPathRow(interface='ether1', disabled=False)),
    ))
def test_isunique(expected, keys, row1, row2):
    assert ( row1.isunique(row2, keys=keys) ) == expected
