# -*- coding: UTF-8 -*-

try:
    from unittest.mock import MagicMock, patch, call, PropertyMock
except ImportError:
    from mock import MagicMock, patch, call, PropertyMock
from unittest import TestCase

from printers import Single, CachedPrint, Generic, Keyed




class CachedPrintTests(TestCase):

    def setUp(self):
        self.TestCls = CachedPrint()
        self.instmock = MagicMock()
        self.ownmock = MagicMock()

    def test_calls_instances_api_run_method(self):
        self.TestCls.__get__(self.instmock, self.ownmock)
        self.assertEqual( self.instmock.api.run.call_count, 1 )

    def test_sets_instances_dictionary_with_data_key_value(self):
        self.instmock.api.run.return_value = 1
        self.TestCls.__get__(self.instmock, self.ownmock)
        self.assertEqual( self.instmock.data, 1 )

    def test_returns_same_data_as_run_method_returns(self):
        self.instmock.api.run.return_value = 1
        retval = self.TestCls.__get__(self.instmock, self.ownmock)
        self.assertEqual( retval, 1 )






@patch.object(Generic, 'data', new_callable=PropertyMock)
class SinglePrinter(TestCase):

    def setUp(self):
        self.TestCls = Single( lvl=None, api=None )

    def test_get_gets_data_from_desctiptor(self, datamock):
        self.TestCls.get()
        self.assertEqual(datamock.call_count, 1)

    def test_get_indexes_first_item(self, datamock):
        mlist = datamock.return_value = MagicMock().__getitem__ = MagicMock()
        self.TestCls.get()
        self.assertEqual(1, mlist.__getitem__.call_count)



class KeyedPrinter(TestCase):

    def setUp(self):
        self.TestCls = Keyed( lvl=None, api=None )

    @patch.object(Generic, 'data', new_callable=PropertyMock)
    @patch.object(Keyed, 'issubset')
    def test_get_calls_issubset(self, submock, datamock):
        datamock.return_value = [1,2,3]
        submock.return_value = False
        self.TestCls.get( 1 )
        self.assertEqual(submock.call_count, 3)

    @patch.object(Generic, 'data', new_callable=PropertyMock)
    @patch.object(Keyed, 'issubset')
    def test_get_returns_first_found_element(self, submock, datamock):
        datamock.return_value = [1,2,3]
        submock.return_value = True
        retval = self.TestCls.get( None )
        self.assertEqual(retval, 1)

    @patch.object(Generic, 'data', new_callable=PropertyMock)
    @patch.object(Keyed, 'issubset')
    def test_get_returns_empty_dict_if_nothing_found(self, submock, datamock):
        submock.return_value = False
        retval = self.TestCls.get( 1 )
        self.assertEqual( retval, dict() )

    def test_issubset_returns_True_if_all_emements_are_in_tested_rule(self):
        rule = {'address': 'x.x', 'disabled': False, 'dynamic': False, 'list': 'testlist'}
        retval = self.TestCls.issubset( {'address':'x.x'}, rule )
        self.assertTrue( retval == True )

    def test_issubset_returns_False_if_emements_not_found_in_tested_rule(self):
        rule = {'address': 'x.x', 'disabled': False, 'dynamic': False, 'list': 'testlist'}
        retval = self.TestCls.issubset( {'address':'x.x.x'}, rule )
        self.assertTrue( retval == False )

