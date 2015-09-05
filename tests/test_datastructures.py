# -*- coding: UTF-8 -*-

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch
from unittest import TestCase

from mcm.datastructures import CmdPathRow, make_cmdpath


@patch('mcm.datastructures.MENU_PATHS')
class CmdPath_Tests(TestCase):

    def test_absolute_attribute_returns_absolute_path_without_appended_forward_slash(self, paths_mock):
        cmd_path = make_cmdpath('/ip/address/', strategy=None)
        self.assertEqual( cmd_path.absolute, '/ip/address' )

    def test_absolute_attribute_returns_absolute_path_when_passed_path_does_not_begin_with_forward_slash(self, paths_mock):
        cmd_path = make_cmdpath('ip/address', strategy=None)
        self.assertEqual( cmd_path.absolute, '/ip/address' )

    def test_absolute_attribute_returns_absolute_path_when_passed_path_begins_with_forward_slash(self, paths_mock):
        cmd_path = make_cmdpath('/ip/address', strategy=None)
        self.assertEqual( cmd_path.absolute, '/ip/address' )

    def test_strategy_attribute_is_the_same_as_passed_in_function_call(self, paths_mock):
        cmd_path = make_cmdpath('/ip/address', strategy='exact')
        self.assertEqual(cmd_path.strategy, 'exact')

    def test_calls_getitem_on_paths_data_structure(self, paths_mock):
        make_cmdpath('/ip/address', strategy='exact')
        paths_mock.__getitem__.assert_called_once_with('/ip/address')

    def test_calling_getitem_on_paths_data_structure_riases_KeyError_when_path_is_missing(self, paths_mock):
        paths_mock.__getitem__.side_effect = KeyError
        with self.assertRaises(KeyError):
            make_cmdpath('/ip/address', 'exact')



class CmdPathRow_Tests(TestCase):

    def setUp(self):
        self.TestCls = CmdPathRow(data=MagicMock())
        self.Other = CmdPathRow(data=MagicMock())

    def test_str_on_instance_returns_string(self):
        self.assertIsInstance( str(self.TestCls), str )

    def test_str_on_instance_returns_substitute_True_with_yes(self):
        row = CmdPathRow(data={'enabled':True})
        self.assertEqual(str(row), 'enabled=yes')

    def test_str_on_instance_returns_substitute_False_with_no(self):
        row = CmdPathRow(data={'enabled':False})
        self.assertEqual(str(row), 'enabled=no')

    def test_equal_returns_True_when_data_is_same(self):
        self.TestCls.data = dict(some_key='value')
        self.Other.data = dict(some_key='value')
        self.assertTrue( self.TestCls == self.Other )

    def test_equal_returns_False_when_data_is_different(self):
        self.TestCls.data = dict(some_key='value1')
        self.Other.data = dict(some_key='value')
        self.assertFalse( self.TestCls == self.Other )

    def test_not_equal_returns_True_when_data_is_different(self):
        self.TestCls.data = dict(some_key='value')
        self.Other.data = dict(some_key='value1')
        self.assertTrue( self.TestCls != self.Other )

    def test_not_equal_returns_False_when_data_is_same(self):
        self.TestCls.data = dict(some_key='value')
        self.Other.data = dict(some_key='value')
        self.assertFalse( self.TestCls != self.Other )

    def test_getting_key_value_gets_from_data(self):
        self.TestCls.data = dict(some_key='value')
        self.assertEqual( self.TestCls['some_key'], 'value' )

    def test_setting_key_sets_data_key(self):
        self.TestCls.data = dict()
        self.TestCls['some_key'] = 'value'
        self.assertEqual( self.TestCls.data['some_key'], 'value' )

    def test_bool_returns_True_if_data_is_not_empty(self):
        self.TestCls.data = dict(interface='ether1')
        self.assertTrue( self.TestCls )

    def test_bool_returns_False_if_data_is_empty(self):
        self.TestCls.data = dict()
        self.assertFalse( self.TestCls )

    @patch.object(CmdPathRow, 'difference')
    def test_sub_calls_difference(self, diffmock):
        self.TestCls - self.Other
        diffmock.assert_called_once_with( wanted=self.TestCls.data, present=self.Other.data )

    @patch.object(CmdPathRow, 'difference', return_value=MagicMock())
    def test_sub_returns_CmdPathRow_instance(self, diffmock):
        returned = self.TestCls - self.Other
        self.assertIsInstance( returned, CmdPathRow )

    @patch.object(CmdPathRow, 'difference', return_value=MagicMock())
    def test_sub_returns_CmdPathRow_instance_with_data_returned_from_difference(self, diffmock):
        datamock = diffmock.return_value = MagicMock()
        returned = self.TestCls - self.Other
        self.assertEqual( returned.data, datamock )

    def test_isunique_returns_True_when_keys_and_its_values_match_in_both_rules(self):
        rule1 = dict(interface='ether2', disabled=False)
        rule2 = dict(interface='ether2', disabled=False)
        self.TestCls.data = rule1
        self.Other.data = rule2
        self.assertTrue( self.TestCls.isunique(self.Other, keys=('interface',)) )

    def test_isunique_returns_True_when_all_keys_and_its_values_match_in_both_rules(self):
        rule1 = dict(interface='ether2', disabled=False)
        rule2 = dict(interface='ether2', disabled=False)
        self.TestCls.data = rule1
        self.Other.data = rule2
        self.assertTrue( self.TestCls.isunique(self.Other, keys=('interface','disabled')) )

    def test_isunique_returns_False_when_keys_and_its_values_do_not_match_in_both_rules(self):
        rule1 = dict(interface='ether1', disabled=False)
        rule2 = dict(interface='ether2', disabled=False)
        self.TestCls.data = rule1
        self.Other.data = rule2
        self.assertFalse( self.TestCls.isunique(self.Other, keys=('interface',)) )

    def test_isunique_returns_False_when_at_least_one_key_value_pait_do_not_match_in_both_rules(self):
        rule1 = dict(interface='ether1', disabled=False)
        rule2 = dict(interface='ether2', disabled=False)
        self.TestCls.data = rule1
        self.Other.data = rule2
        self.assertFalse( self.TestCls.isunique(self.Other, keys=('interface','disabled')) )

    def test_difference_returns_elements_in_wanted_not_listed_in_present(self):
        wanted = dict(interface='ether1')
        present = dict(interface='ether2')
        result = self.TestCls.difference( wanted=wanted, present=present  )
        self.assertEqual( result, dict(interface='ether1') )
