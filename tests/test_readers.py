# -*- coding: UTF-8 -*-

try:
    from unittest.mock import MagicMock, patch, PropertyMock
except ImportError:
    from mock import MagicMock, patch, PropertyMock
from unittest import TestCase

from readers import CachedRead, ApiReader




class CachedReadTests(TestCase):

    def setUp(self):
        self.TestCls = CachedRead()
        self.instmock = MagicMock()
        self.instmock.path.getall = '/some/path/getall'

    @patch.object(CachedRead, 'filter')
    def test_getter_calls_instances_api_run_method(self,filtermock):
        self.TestCls.__get__(self.instmock, None)
        self.instmock.api.run.assert_called_once_with( self.instmock.path.getall )

    @patch.object(CachedRead, 'filter')
    def test_getter_sets_instances_data_attribute_with_filtered_data_set(self, filtermock):
        filtermock.return_value = 1
        self.TestCls.__get__(self.instmock, None)
        self.assertEqual( self.instmock.data, 1 )

    @patch.object(CachedRead, 'filter')
    def test_getter_calls_filter_with_api_run_returned_data(self, filtermock):
        self.instmock.api.run.return_value = (1,2,3)
        self.TestCls.__get__(self.instmock, None)
        filtermock.assert_called_once_with( (1,2,3) )

    def test_filter_filters_out_dynamic_rules(self):
        data = ( {'dynamic':True, 'name':'asd'}, {'dynamic':False, 'name':'dsa'} )
        retval = self.TestCls.filter( data )
        self.assertEqual( retval, ( {'dynamic':False, 'name':'dsa'}, ) )

    def test_filter_returns_same_data_if_rules_do_not_have_dynamic_key(self):
        data = ( {'name':'asd'}, {'name':'dsa'} )
        retval = self.TestCls.filter( data )
        self.assertEqual( retval, data )



class ApiReaderTests(TestCase):

    def setUp(self):
        self.TestCls = ApiReader( path=None, api=None )

    @patch.object(CachedRead, '__get__')
    def test_accessing_data_attribute_calls_data_descriptor(self, datamock):
        self.TestCls.data
        self.assertEqual( datamock.call_count, 1 )

    def test_issubset_returns_True_if_all_key_value_pairs_are_present_in_tested_rule(self):
        rule = {'address': 'x.x', 'disabled': False, 'dynamic': False, 'list': 'testlist'}
        retval = self.TestCls.issubset( {'address':'x.x', 'disabled':False}, rule )
        self.assertTrue( retval == True )

    def test_issubset_returns_False_if_at_least_one_key_value_pair_is_not_present_in_tested_rule(self):
        rule = {'address': 'x.x', 'disabled': False, 'dynamic': False, 'list': 'testlist'}
        retval = self.TestCls.issubset( {'address':'x.x', 'disabled':True}, rule )
        self.assertTrue( retval == False )

    @patch.object(ApiReader, 'data', new_callable=PropertyMock, return_value=[1]*100)
    @patch.object(ApiReader, 'issubset')
    def test_get_calls_issubset_untill_first_matching_subset_is_found(self, subsetmock, datamock):
        subsetmock.side_effect = [False, False, True, False]
        self.TestCls.get( dict() )
        self.assertEqual(subsetmock.call_count, 3)

    @patch.object(ApiReader, 'data', new_callable=PropertyMock, return_value=[1]*100)
    @patch.object(ApiReader, 'issubset')
    def test_get_returns_empty_dict_if_no_match_have_been_found(self, subsetmock, datamock):
        subsetmock.return_value = False
        retval = self.TestCls.get( dict() )
        self.assertEqual( retval, dict() )

