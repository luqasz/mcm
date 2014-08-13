# -*- coding: UTF-8 -*-

try:
    from unittest.mock import MagicMock, patch, PropertyMock
except ImportError:
    from mock import MagicMock, patch
from unittest import TestCase


from cmdpath import UniqueKeyCmdPath, SingleElementCmdPath, GenericCmdPath, mkCmdPath, OrderedCmdPath
from datastructures import CmdPathElem


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



class GenericCmdPath_Tests(TestCase):

    def setUp(self):
        DataMock = MagicMock()
        self.DataElemMock = MagicMock()
        DataMock.__iter__.return_value = iter( [self.DataElemMock] )

        self.TestCls = GenericCmdPath( data=DataMock )
        self.TestCls.SET = MagicMock()
        self.SETElemMock = MagicMock()
        self.TestCls.SET.__iter__.return_value = iter( [self.SETElemMock] )

        self.TestCls.DEL = MagicMock()
        self.TestCls.ADD = MagicMock()
        self.Diffmock = MagicMock()
        self.PresentMock = MagicMock()

    def test_decide_calls_appen_on_ADD_when_not_present_and_difference(self):
        self.TestCls.decide( self.Diffmock, None )
        self.TestCls.ADD.append.assert_called_once_with( self.Diffmock )

    def test_decide_calls_append_on_DEL_when_not_difference_and_present(self):
        self.TestCls.decide( None, self.PresentMock )
        self.TestCls.DEL.append.assert_called_once_with( self.PresentMock )

    def test_decide_calls_append_on_SET_when_difference_and_present(self):
        self.TestCls.decide( self.Diffmock, self.PresentMock )
        self.TestCls.SET.append.assert_called_once_with( (self.PresentMock,self.Diffmock) )

    def test_decide_calls_getitem_on_present_when_difference_and_present(self):
        self.TestCls.decide( self.Diffmock, self.PresentMock )
        self.PresentMock.__getitem__.assert_called_once_with( 'ID' )

    def test_decide_calls_setitem_on_difference_when_difference_and_present(self):
        id = self.PresentMock.__getitem__.return_value = MagicMock()
        self.TestCls.decide( self.Diffmock, self.PresentMock )
        self.Diffmock.__setitem__.assert_called_once_with( 'ID', id )

    def test_decide_getitem_on_present_when_raises_KeyError_does_not_call_setitem_on_difference(self):
        self.PresentMock.__getitem__.side_effect = KeyError
        self.TestCls.decide( self.Diffmock, self.PresentMock )
        self.assertEqual( self.Diffmock.__setitem__.call_count, 0 )

    def test_populateDEL_iterates_over_data(self):
        self.TestCls.populateDEL()
        self.TestCls.data.__iter__.assert_called_once_with()

    def test_populateDEL_iterates_over_SET(self):
        self.TestCls.populateDEL()
        self.TestCls.SET.__iter__.assert_called_once_with()

    def test_populateDEL_calls_getitem_0_on_element_in_SET(self):
        self.TestCls.populateDEL()
        self.SETElemMock.__getitem__.assert_called_once_with( 0 )

    def test_populateDEL_calls_append_on_DEL_if_row_from_data_is_found_in_SET(self):
        self.DataElemMock.__eq__.return_value = True
        self.TestCls.populateDEL()
        self.TestCls.DEL.append.assert_any_call( self.DataElemMock )

    def test_populateDEL_does_not_call_append_on_DEL_if_row_is_not_found_in_SET(self):
        self.DataElemMock.__eq__.return_value = False
        self.TestCls.populateDEL()
        self.assertEqual( self.TestCls.DEL.append.call_count, 0 )




@patch('cmdpath.zip_longest', return_value=MagicMock() )
@patch.object(GenericCmdPath, 'decide')
@patch.object(GenericCmdPath, 'populateDEL')
class OrderedCmdPath_Tests(TestCase):

    def setUp(self):
        self.DataMock = MagicMock()
        self.wanted = MagicMock()
        self.TestCls = OrderedCmdPath( data=self.DataMock )

    def test_compare_calls_populateDEL(self, populatemock, decidemock, zipmock):
        self.TestCls.compare( self.wanted )
        populatemock.assert_called_once_with()

    def test_compare_returns_ADD_SET_DEL_in_order(self, populatemock, decidemock, zipmock):
        data = self.TestCls.compare( self.wanted )
        self.assertEqual( data, (self.TestCls.ADD, self.TestCls.SET, self.TestCls.DEL) )

    def test_compare_calls_zip_longest_with_wanted_and_present(self, populatemock, decidemock, zipmock):
        self.TestCls.compare( self.wanted )
        fillobj = CmdPathElem( data=dict(), keys=tuple(), split_map=dict() )
        zipmock.assert_called_once_with( self.DataMock, self.wanted, fillvalue=fillobj )

    def test_compare_calls_sub_on_wanted(self, populatemock, decidemock, zipmock):
        wanted_mock = MagicMock(name='wanted_mock')
        present_mock = MagicMock(name='present_mock')
        zipmock.return_value.__iter__.return_value = [( present_mock, wanted_mock )]
        self.TestCls.compare( self.wanted )
        wanted_mock.__sub__.assert_called_once_with( present_mock )

    def test_compare_calls_decide(self, populatemock, decidemock, zipmock):
        wanted_mock = MagicMock(name='wanted_mock')
        diff = wanted_mock.__sub__.return_value = MagicMock()
        present_mock = MagicMock(name='present_mock')
        zipmock.return_value.__iter__.return_value = [( present_mock, wanted_mock )]
        self.TestCls.compare( self.wanted )
        decidemock.assert_called_once_with( difference=diff, present=present_mock )




class SingleElementCmdPath_Tests(TestCase):

    def setUp(self):
        self.Wanted = MagicMock()
        self.WantedElem = MagicMock()
        self.Wanted.__getitem__.return_value = self.WantedElem
        self.DataMock = MagicMock()
        self.DateElemMock = MagicMock()
        self.DataMock.__getitem__.return_value = self.DateElemMock
        self.TestCls = SingleElementCmdPath( data=self.DataMock )

    @patch.object(GenericCmdPath, 'decide')
    @patch.object(GenericCmdPath, 'populateDEL')
    def test_compare_does_not_call_populateDEL(self, populatemock, decidemock):
        self.TestCls.compare( self.Wanted )
        self.assertEqual( populatemock.call_count, 0 )

    @patch.object(GenericCmdPath, 'decide')
    def test_compare_returns_ADD_SET_DEL_in_order(self, decidemock):
        data = self.TestCls.compare( self.Wanted )
        self.assertEqual( data, (self.TestCls.ADD, self.TestCls.SET, self.TestCls.DEL) )

    @patch.object(GenericCmdPath, 'decide')
    def test_compare_calls_getitem_on_wanted(self, decidemock):
        self.TestCls.compare( self.Wanted )
        self.Wanted.__getitem__.assert_called_once_with(0)

    @patch.object(GenericCmdPath, 'decide')
    def test_compare_calls_getitem_on_data(self, decidemock):
        self.TestCls.compare( self.Wanted )
        self.DataMock.__getitem__.assert_called_once_with(0)

    @patch.object(GenericCmdPath, 'decide')
    def test_compare_calls_sub_on_WantedElem(self, decidemock):
        self.TestCls.compare( self.Wanted )
        self.WantedElem.__sub__.assert_called_once_with(self.DateElemMock)

    @patch.object(GenericCmdPath, 'decide')
    def test_compare_calls_decide_with_sub_result_and_present(self, decidemock):
        diffmock = self.WantedElem.__sub__.return_value = MagicMock()
        self.TestCls.compare( self.Wanted )
        decidemock.assert_called_once_with( diffmock, self.DateElemMock )

    @patch.object(GenericCmdPath, 'decide')
    def test_compare_does_not_iterate_over_wanted(self, decidemock):
        self.TestCls.compare( self.Wanted )
        self.assertEqual( self.Wanted.__iter__.call_count, 0)

    @patch.object(GenericCmdPath, 'decide')
    def test_compare_does_not_iterate_over_data(self, decidemock):
        self.TestCls.compare( self.Wanted )
        self.assertEqual( self.DataMock.__iter__.call_count, 0)


class UniqueKeyCmdPath_Tests(TestCase):

    def setUp(self):
        self.RuleMock = MagicMock()
        self.Wanted = MagicMock()
        self.WantedElem = MagicMock()
        self.Wanted.__iter__.return_value = iter([ self.WantedElem ])
        self.DataMock = MagicMock()
        self.DateElemMock = MagicMock()
        self.DataMock.__iter__.return_value = iter([ self.DateElemMock ])
        self.TestCls = UniqueKeyCmdPath( data=self.DataMock )

    @patch.object(UniqueKeyCmdPath, 'search')
    @patch.object(GenericCmdPath, 'populateDEL')
    @patch.object(GenericCmdPath, 'decide')
    def test_compare_iterates_over_wanted(self, decidemock, populatemock, searchmock):
        self.TestCls.compare(self.Wanted)
        self.Wanted.__iter__.assert_called_once_with()

    @patch.object(UniqueKeyCmdPath, 'search')
    @patch.object(GenericCmdPath, 'populateDEL')
    @patch.object(GenericCmdPath, 'decide')
    def test_compare_calls_search_with_rule(self, decidemock, populatemock, searchmock):
        self.TestCls.compare(self.Wanted)
        searchmock.assert_any_call( self.WantedElem )

    @patch.object(UniqueKeyCmdPath, 'search')
    @patch.object(GenericCmdPath, 'populateDEL')
    @patch.object(GenericCmdPath, 'decide')
    def test_compare_returns_ADD_SET_DEL_in_order(self, decidemock, populatemock, searchmock):
        data = self.TestCls.compare( self.Wanted )
        self.assertEqual( data, (self.TestCls.ADD, self.TestCls.SET, self.TestCls.DEL) )

    @patch.object(UniqueKeyCmdPath, 'search')
    @patch.object(GenericCmdPath, 'populateDEL')
    @patch.object(GenericCmdPath, 'decide')
    def test_compare_calls_sub_on_WantedElem(self, decidemock, populatemock, searchmock):
        found = searchmock.return_value = MagicMock()
        self.TestCls.compare(self.Wanted)
        self.WantedElem.__sub__.assert_any_call( found )

    @patch.object(UniqueKeyCmdPath, 'search')
    @patch.object(GenericCmdPath, 'populateDEL')
    @patch.object(GenericCmdPath, 'decide')
    def test_compare_calls_decide_with_sub_result_and_present(self, decidemock, populatemock, searchmock):
        result = self.WantedElem.__sub__.return_value = MagicMock()
        found = searchmock.return_value = MagicMock()
        self.TestCls.compare(self.Wanted)
        decidemock.assert_any_call( result, found )

    @patch.object(UniqueKeyCmdPath, 'search')
    @patch.object(GenericCmdPath, 'populateDEL')
    @patch.object(GenericCmdPath, 'decide')
    def test_compare_calls_populateDEL(self, decidemock, populatemock, searchmock):
        self.TestCls.compare(self.Wanted)
        populatemock.assert_called_once_with()

    @patch.object(UniqueKeyCmdPath, 'search')
    @patch.object(GenericCmdPath, 'populateDEL')
    @patch.object(GenericCmdPath, 'decide')
    def test_compare_does_not_iterate_over_data(self, decidemock, populatemock, searchmock):
        self.TestCls.compare( self.Wanted )
        self.assertEqual( self.DataMock.__iter__.call_count, 0)

    def test_search_returns_CmdPathElem_instane_if_no_match_have_been_found(self):
        self.DateElemMock.isunique.return_value = False
        retval = self.TestCls.search( self.RuleMock )
        self.assertIsInstance( retval, CmdPathElem )

    def test_search_calls_DataElem_isunique(self):
        self.TestCls.search( self.RuleMock )
        self.DateElemMock.isunique.assert_called_once_with( self.RuleMock )

