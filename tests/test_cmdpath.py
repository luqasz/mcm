# -*- coding: UTF-8 -*-

try:
    from unittest.mock import MagicMock, patch, PropertyMock
except ImportError:
    from mock import MagicMock, patch, PropertyMock
from unittest import TestCase


# mock whole module since it may be unavailable on some machines
librouteros_mock = MagicMock()
mp = patch.dict('sys.modules', {'librouteros.extras':librouteros_mock})
mp.start()

from cmdpath import UniqueKeyCmdPath, SingleElementCmdPath, GenericCmdPath, mkCmdPath


class PathTests(TestCase):

    def setUp(self):
        self.menu_attributes = { 'type':'withkey', 'modord':['set', 'add', 'del'], 'keys': ['name'], 'split_by':'', 'split_keys':[] }
        self.path = '/ip/address'
        self.menu_path = mkCmdPath( path=self.path, attrs=self.menu_attributes )

    def test_path_attribute_returns_absolute_path_without_appended_forward_slash(self):
        self.assertEqual( self.menu_path.path, '/ip/address' )

    def test_path_attribute_returns_absolute_path_when_passed_path_does_not_begin_with_forward_slash(self):
        self.path = 'ip/address'
        self.assertEqual( self.menu_path.path, '/ip/address' )

    def test_path_attribute_returns_absolute_path_when_passed_path_begins_with_forward_slash(self):
        self.path = '/ip/address'
        self.assertEqual( self.menu_path.path, '/ip/address' )

    def test_remove_returns_appended_remove_string_without_ending_forward_slash(self):
        self.assertEqual( self.menu_path.remove, '/ip/address/remove' )

    def test_add_returns_appended_add_string_without_ending_forward_slash(self):
        self.assertEqual( self.menu_path.add, '/ip/address/add' )

    def test_set_returns_appended_set_string_without_ending_forward_slash(self):
        self.assertEqual( self.menu_path.set, '/ip/address/set' )

    def test_getall_returns_appended_getall_string_without_ending_forward_slash(self):
        self.assertEqual( self.menu_path.getall, '/ip/address/getall' )

    def test_type_returns_same_value_as_passed_in_attrs_dictionary(self):
        self.assertEqual( self.menu_path.type, self.menu_attributes['type'] )

    def test_modord_returns_same_value_as_passed_in_attrs_dictionary(self):
        self.assertEqual( self.menu_path.modord, self.menu_attributes['modord'] )

    def test_keys_returns_same_value_as_passed_in_attrs_dictionary(self):
        self.assertEqual( self.menu_path.keys, self.menu_attributes['keys'] )

    def test_split_by_returns_same_value_as_passed_in_attrs_dictionary(self):
        self.assertEqual( self.menu_path.split_by, self.menu_attributes['split_by'] )

    def test_split_keys_returns_same_value_as_passed_in_attrs_dictionary(self):
        self.assertEqual( self.menu_path.split_keys, self.menu_attributes['split_keys'] )



class GenericCmdPath_decide_Tests(TestCase):

    def setUp(self):
        self.ApiReadermock = MagicMock()
        self.wanted = ( MagicMock(), MagicMock() )
        self.TestCls = GenericCmdPath( printer=self.ApiReadermock, keys=None, )

    def test_decide_appends_to_SET_with_ID_if_difference_and_non_empty_present(self):
        self.TestCls.decide( difference={'name':1}, present={'ID':1, 'name':2} )
        self.assertEqual( [ {'ID':1, 'name':1} ], self.TestCls.SET )

    def test_decide_appends_to_ADD_if_difference_and_empty_present(self):
        self.TestCls.decide( difference={'name':1}, present=dict() )
        self.assertEqual( [ {'name':1} ], self.TestCls.ADD )

    def test_decide_does_not_append_to_ADD_if_no_difference(self):
        self.TestCls.decide( difference=dict(), present={'ID':1, 'name':1} )
        self.assertEqual( [], self.TestCls.ADD )

    def test_decide_does_not_append_to_SET_if_no_difference(self):
        self.TestCls.decide( difference=dict(), present={'ID':1, 'name':1} )
        self.assertEqual( [], self.TestCls.SET )


@patch('cmdpath.dictdiff')
@patch.object(GenericCmdPath, 'decide')
@patch.object(GenericCmdPath, 'purge')
class GenericCmdPath_compare_Tests(TestCase):

    def setUp(self):
        self.ApiReadermock = MagicMock()
        self.ReaderDataMock = PropertyMock( return_value=[1]*10 )
        type(self.ApiReadermock).data = self.ReaderDataMock
        self.wanted = ( MagicMock(), MagicMock() )
        self.TestCls = GenericCmdPath( printer=self.ApiReadermock, keys=None, )

    def test_compare_calls_purge(self, purgemock, decidemock, diffmock):
        self.TestCls.compare( self.wanted )
        purgemock.assert_called_once_with()

    def test_compare_accesses_Printers_data_attribute(self, purgemock, decidemock, diffmock):
        self.TestCls.compare( self.wanted )
        self.ReaderDataMock.assert_called_once_with()

    def test_compare_calls_dictdiff_for_longest_iterable_present_rules(self, purgemock, decidemock, diffmock):
        self.ApiReadermock.get.return_value = [1] * 10
        self.TestCls.compare( [1] )
        self.assertEqual( diffmock.call_count, 10 )

    def test_compare_calls_dictdiff_for_longest_iterable_wanted(self, purgemock, decidemock, diffmock):
        self.ApiReadermock.get.return_value = [1]
        self.TestCls.compare( [1]*10 )
        self.assertEqual( diffmock.call_count, 10 )

    def test_compare_calls_decide_for_longest_iterable_present_rules(self, purgemock, decidemock, diffmock):
        self.ApiReadermock.get.return_value = [1] * 10
        self.TestCls.compare( [1] )
        self.assertEqual( decidemock.call_count, 10 )

    def test_compare_calls_decide_for_longest_iterable_wanted(self, purgemock, decidemock, diffmock):
        self.ApiReadermock.get.return_value = [1]
        self.TestCls.compare( [1]*10 )
        self.assertEqual( decidemock.call_count, 10 )



@patch('cmdpath.dictdiff')
class SingleElementCmdPathTests(TestCase):

    def setUp(self):
        self.ApiReadermock = MagicMock()
        self.wanted = MagicMock()
        self.TestCls = SingleElementCmdPath( printer=self.ApiReadermock, keys=tuple(), )

    def test_compare_does_not_modify_DEL(self, diffmock):
        self.TestCls.compare( self.wanted )
        self.assertEqual( self.TestCls.DEL, list() )

    def test_compare_does_not_modify_ADD(self, diffmock):
        self.TestCls.compare( self.wanted )
        self.assertEqual( self.TestCls.ADD, list() )

    def test_compare_calls_dictdiff_with_extracted_first_element(self, diffmock):
        self.ApiReadermock.get.return_value = ('get_value', )
        self.TestCls.compare( self.wanted )
        diffmock.assert_called_once_with(wanted=self.wanted, present='get_value')

    def test_compare_calls_printers_get_method(self, diffmock):
        self.TestCls.compare( self.wanted )
        self.ApiReadermock.get.assert_called_once_with()

    def test_compare_updates_SET_if_difference(self, diffmock):
        diffmock.return_value = self.wanted
        self.TestCls.compare( self.wanted )
        self.assertEqual( [self.wanted], self.TestCls.SET )

    def test_compare_does_not_update_SET_if_no_difference(self, diffmock):
        diffmock.return_value = dict()
        self.TestCls.compare( self.wanted )
        self.assertEqual( self.TestCls.SET, list() )



@patch.object(GenericCmdPath, 'purge')
@patch.object(GenericCmdPath, 'decide')
@patch.object(UniqueKeyCmdPath, 'mkkvp')
@patch('cmdpath.dictdiff')
class UniqueKeyCmdPath_compare_Tests(TestCase):

    def setUp(self):
        self.ApiReadermock = MagicMock()
        self.wanted = ( MagicMock(), MagicMock() )
        self.TestCls = UniqueKeyCmdPath( printer=self.ApiReadermock, keys=('name',), )

    def test_compare_calls_printers_get_method(self, diffmock, mkkvpmock, decidemock, purgemock):
        self.TestCls.compare(self.wanted)
        self.assertEqual( self.ApiReadermock.get.call_count, 2 )

    def test_compare_calls_dictdiff(self, diffmock, mkkvpmock, decidemock, purgemock):
        self.TestCls.compare(self.wanted)
        self.assertEqual( diffmock.call_count, 2 )

    def test_compare_calls_purge(self, diffmock, mkkvpmock, decidemock, purgemock):
        self.TestCls.compare(self.wanted)
        purgemock.assert_called_once_with()

    def test_compare_calls_mkkvp(self, diffmock, mkkvpmock, decidemock, purgemock):
        self.TestCls.compare(self.wanted)
        self.assertEqual( mkkvpmock.call_count, 2 )

    def test_compare_calls_decide(self, diffmock, mkkvpmock, decidemock, purgemock):
        self.TestCls.compare(self.wanted)
        self.assertEqual( decidemock.call_count, 2 )


class UniqueKeyCmdPath_mkkvp_Tests(TestCase):

    def setUp(self):
        self.ApiReadermock = MagicMock()
        self.wanted = ( MagicMock(), MagicMock() )
        self.TestCls = UniqueKeyCmdPath( printer=self.ApiReadermock, keys=('name',), )

    def test_mkkvp_extracts_key_value_pair_when_keys_have_one_element(self):
        self.TestCls.keys = ('name',)
        kvp = self.TestCls.mkkvp( {'name':'some_name', 'ID':2} )
        self.assertEqual( {'name':'some_name'}, kvp )

    def test_mkkvp_extracts_key_value_pairs_when_keys_have_multiple_elements(self):
        self.TestCls.keys = ('name','address')
        kvp = self.TestCls.mkkvp( {'name':'some_name', 'address':'1.1.1.1', 'ID':2} )
        self.assertEqual( {'name':'some_name','address':'1.1.1.1'}, kvp )
