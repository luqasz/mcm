# -*- coding: UTF-8 -*-

try:
    from unittest.mock import MagicMock, patch, PropertyMock
except ImportError:
    from mock import MagicMock, patch, PropertyMock
from unittest import TestCase

from datastructures import CmdPathElem

class CmdPathElemTests(TestCase):

    def setUp(self):
        self.TestCls = CmdPathElem(data=MagicMock(), keys=MagicMock(), split_pairs=MagicMock())
        self.Other = CmdPathElem(data=MagicMock(), keys=MagicMock(), split_pairs=MagicMock())

    def test_str_on_class_converts_its_data_into_printable_form(self):
        self.assertIsInstance( str(self.TestCls), str )

    def test_equal_calls_eq_magic_method_on_data(self):
        self.TestCls == self.Other
        self.TestCls.data.__eq__.assert_called_once_with(self.Other.data)

    def test_not_equal_calls_ne_magic_method_on_data(self):
        self.TestCls != self.Other
        self.TestCls.data.__ne__.assert_called_once_with(self.Other.data)

    def test_hash_calls_hash_magic_method_on_data(self):
        hash(self.TestCls)
        self.TestCls.data.__hash__.assert_called_once_with()

    def test_iter_calls_iter_magic_method_on_data(self):
        iter(self.TestCls)
        self.TestCls.data.__iter__.assert_called_once_with()

    @patch.object(CmdPathElem, 'difference')
    def test_sub_operator_calls_diff(self, diffmock):
        self.TestCls - self.Other
        diffmock.assert_called_once_with(self.Other)

    def test_computes_difference_between_two_strings(self):
        retval = CmdPathElem.strdiff( '1,2,3', '1', ',' )
        # this variable must be as is. python is unpredictable how it will order hashed items
        desired = ','.join( {'3','2'} )
        self.assertEqual( retval, desired )

