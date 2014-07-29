# -*- coding: UTF-8 -*-

try:
    from unittest.mock import MagicMock, patch, PropertyMock
except ImportError:
    from mock import MagicMock, patch, PropertyMock
from unittest import TestCase

from datastructures import CmdPathElem

class CmdPathElemTests(TestCase):

    def setUp(self):
        self.TestCls = CmdPathElem(data=MagicMock(), keys=MagicMock(), split_map=MagicMock())
        self.Other = CmdPathElem(data=MagicMock(), keys=MagicMock(), split_map=MagicMock())

    def test_str_on_class_converts_its_data_into_printable_form(self):
        self.assertIsInstance( str(self.TestCls), str )

    def test_equal_calls_eq_magic_method_on_data(self):
        self.TestCls == self.Other
        self.TestCls.data.__eq__.assert_called_once_with(self.Other.data)

    def test_not_equal_calls_ne_magic_method_on_data(self):
        self.TestCls != self.Other
        self.TestCls.data.__ne__.assert_called_once_with(self.Other.data)

    def test_iter_calls_items_view_of_data(self):
        iter(self.TestCls)
        self.TestCls.data.items.assert_called_once_with()

    @patch.object(CmdPathElem, 'difference')
    def test_sub_calls_difference(self, diffmock):
        self.TestCls - self.Other
        diffmock.assert_called_once_with( wanted=self.TestCls.data, present=self.Other.data, split_map=self.TestCls.split_map )

    @patch.object(CmdPathElem, 'difference', return_value=MagicMock())
    def test_sub_returns_CmdPathElem_instance(self, diffmock):
        returned = self.TestCls - self.Other
        self.assertIsInstance( returned, CmdPathElem )

    def test_difference_returns_elements_in_wanted_not_listed_in_present(self):
        wanted = dict(interface='ether1')
        present = dict(interface='ether2')
        result = CmdPathElem.difference( wanted=wanted, present=present)
        self.assertEqual( result, dict(interface='ether1') )

    @patch.object(CmdPathElem, 'strdiff', return_value=MagicMock())
    def test_difference_calls_strdiff_when_split_map_is_provided(self, strdiffmock):
        wanted = dict(attrs='1,2,3', interface='ether1')
        present = dict(attrs='1,2', interface='ether1')
        CmdPathElem.difference( wanted=wanted, present=present, split_map={'attrs':','} )
        strdiffmock.assert_called_once_with( '1,2,3', '1,2', ',' )

    def test_strdiff_returns_elements_from_wanted_not_listed_in_present(self):
        retval = CmdPathElem.strdiff( '1,2,3', '1', ',' )
        # this variable must be as is. python is unpredictable how it will order hashed items
        desired = ','.join( {'3','2'} )
        self.assertEqual( retval, desired )

    def test_getitem_calls_getitem_on_data(self):
        self.TestCls['some_key']
        self.TestCls.data.__getitem__.assert_called_once_with( 'some_key' )

    def test_bool_calls_bool_on_data(self):
        bool(self.TestCls)
        self.TestCls.data.__bool__.assert_called_once_with()
