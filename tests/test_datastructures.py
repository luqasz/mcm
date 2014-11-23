# -*- coding: UTF-8 -*-

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch
from unittest import TestCase

from datastructures import CmdPathRow, CmdPath



class CmdPath_Tests(TestCase):

    def setUp(self):
        self.cmd_path = CmdPath(base='/ip/address')

    def test_path_attribute_returns_absolute_path_without_appended_forward_slash(self):
        self.cmd_path = CmdPath(base='/ip/address/')
        self.assertEqual( self.cmd_path.base, '/ip/address' )

    def test_path_attribute_returns_absolute_path_when_passed_path_does_not_begin_with_forward_slash(self):
        self.cmd_path = CmdPath(base='ip/address')
        self.assertEqual( self.cmd_path.base, '/ip/address' )

    def test_path_attribute_returns_absolute_path_when_passed_path_begins_with_forward_slash(self):
        self.cmd_path = CmdPath(base='/ip/address')
        self.assertEqual( self.cmd_path.base, '/ip/address' )

    def test_remove_returns_appended_remove_string_without_ending_forward_slash(self):
        self.assertEqual( self.cmd_path.remove, '/ip/address/remove' )

    def test_add_returns_appended_add_string_without_ending_forward_slash(self):
        self.assertEqual( self.cmd_path.add, '/ip/address/add' )

    def test_set_returns_appended_set_string_without_ending_forward_slash(self):
        self.assertEqual( self.cmd_path.set, '/ip/address/set' )

    def test_getall_returns_appended_getall_string_without_ending_forward_slash(self):
        self.assertEqual( self.cmd_path.getall, '/ip/address/getall' )




class CmdPathRow_Tests(TestCase):

    def setUp(self):
        self.TestCls = CmdPathRow(data=MagicMock())
        self.Other = CmdPathRow(data=MagicMock())

    def test_str_on_instance_returns_string(self):
        self.assertIsInstance( str(self.TestCls), str )

    def test_str_on_instance_calls_data_items_method(self):
        str(self.TestCls)
        self.TestCls.data.items.assert_called_once_with()

    def test_equal_calls_eq_magic_method_on_data(self):
        self.TestCls == self.Other
        self.TestCls.data.__eq__.assert_called_once_with(self.Other.data)

    def test_not_equal_calls_ne_magic_method_on_data(self):
        self.TestCls != self.Other
        self.TestCls.data.__ne__.assert_called_once_with(self.Other.data)

    def test_getitem_calls_getitem_on_data(self):
        self.TestCls['some_key']
        self.TestCls.data.__getitem__.assert_called_once_with( 'some_key' )

    def test_setitem_calls_setitem_on_data(self):
        self.TestCls['some_key'] = 'value'
        self.TestCls.data.__setitem__.assert_called_once_with( 'some_key', 'value' )

    def test_bool_calls_bool_on_data(self):
        bool(self.TestCls)
        self.TestCls.data.__bool__.assert_called_once_with()

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

    def test_difference_returns_elements_in_wanted_not_listed_in_present(self):
        wanted = dict(interface='ether1')
        present = dict(interface='ether2')
        result = CmdPathRow.difference( wanted=wanted, present=present  )
        self.assertEqual( result, dict(interface='ether1') )
