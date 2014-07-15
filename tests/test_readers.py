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


