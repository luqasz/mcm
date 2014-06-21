# -*- coding: UTF-8 -*-

try:
    from unittest.mock import MagicMock, patch, call
except ImportError:
    from mock import MagicMock, patch, call
from unittest import TestCase


# mock whole module since it may be unavailable on some machines
librouteros_mock = MagicMock()
mp = patch.dict('sys.modules', {'librouteros.extras':librouteros_mock})
mp.start()

from menus import WithKeyMenu, SingleMenu, GenericMenu, mkpath


class PathTests(TestCase):

    def setUp(self):
        self.path = mkpath( 'ip/address' )

    def test_path_attribute_returns_absolute_path_without_appended_forward_slash(self):
        self.assertEqual( self.path.path, '/ip/address' )

    def test_remove_returns_appended_remove_string_without_ending_forward_slash(self):
        self.assertEqual( self.path.remove, '/ip/address/remove' )

    def test_add_returns_appended_add_string_without_ending_forward_slash(self):
        self.assertEqual( self.path.add, '/ip/address/add' )

    def test_set_returns_appended_set_string_without_ending_forward_slash(self):
        self.assertEqual( self.path.set, '/ip/address/set' )

    def test_getall_returns_appended_getall_string_without_ending_forward_slash(self):
        self.assertEqual( self.path.getall, '/ip/address/getall' )



class GenericMenu_decide_Tests(TestCase):

    def setUp(self):
        self.PrinterMock = MagicMock()
        self.wanted = ( MagicMock(), MagicMock() )
        self.TestCls = GenericMenu( printer=self.PrinterMock, keys=None, exact=True )

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

class GenericMenu_saveDecide_Tests(TestCase):

    def setUp(self):
        self.PrinterMock = MagicMock()
        self.wanted = ( MagicMock(), MagicMock() )
        self.TestCls = GenericMenu( printer=self.PrinterMock, keys=None, exact=True )

    def test_saveDecide_appends_presents_ID_to_SAVE_IDS_when_present_has_ID(self):
        self.TestCls.saveDecide( present={'ID':1, 'name':'some_name'} )
        self.assertEqual( [1], self.TestCls.SAVE_IDS )

    def test_saveDecide_does_not_append_ID_to_SAVE_IDS_when_present_lacks_ID_key(self):
        self.TestCls.saveDecide( present={'name':'some_name'} )
        self.assertEqual( [], self.TestCls.SAVE_IDS )

    def test_saveDecide_does_not_append_ID_to_SAVE_IDS_when_present_is_empty(self):
        self.TestCls.saveDecide( present=dict() )
        self.assertEqual( [], self.TestCls.SAVE_IDS )

class GenericMenu_purge_Tests(TestCase):

    def setUp(self):
        self.PrinterMock = MagicMock()
        self.wanted = ( MagicMock(), MagicMock() )
        self.TestCls = GenericMenu( printer=self.PrinterMock, keys=None, exact=True )

    def test_purge_calls_printers_exceptIDs_method_if_exact_is_True(self):
        self.TestCls.purge()
        self.assertEqual( self.PrinterMock.exceptIDs.call_count, 1 )

    def test_purge_sets_DEL_if_exact_is_True(self):
        self.PrinterMock.exceptIDs.return_value = [ 1,2,3 ]
        self.TestCls.purge()
        self.assertEqual( self.TestCls.DEL, [1,2,3] )

    def test_purge_leaves_DEL_empty_if_exact_is_False(self):
        self.TestCls.exact = False
        self.TestCls.purge()
        self.assertEqual( self.TestCls.DEL, [] )

    def test_purge_does_not_call_printers_exceptIDs_method_if_exact_is_False(self):
        self.TestCls.exact = False
        self.TestCls.purge()
        self.assertEqual( self.PrinterMock.exceptIDs.call_count , 0 )

@patch('menus.dictdiff')
@patch.object(GenericMenu, 'decide')
@patch.object(GenericMenu, 'saveDecide')
@patch.object(GenericMenu, 'purge')
class GenericMenu_compare_Tests(TestCase):

    def setUp(self):
        self.PrinterMock = MagicMock()
        self.wanted = ( MagicMock(), MagicMock() )
        self.TestCls = GenericMenu( printer=self.PrinterMock, keys=None, exact=True )

    def test_compare_calls_purge(self, purgemock, savemock, decidemock, diffmock):
        self.TestCls.compare( self.wanted )
        purgemock.assert_called_once_with()

    def test_compare_calls_Printers_get_method(self, purgemock, savemock, decidemock, diffmock):
        self.TestCls.compare( self.wanted )
        self.PrinterMock.get.assert_called_once_with()

    def test_compare_calls_dictdiff_for_longest_iterable_present_rules(self, purgemock, savemock, decidemock, diffmock):
        self.PrinterMock.get.return_value = [1] * 10
        self.TestCls.compare( [1] )
        self.assertEqual( diffmock.call_count, 10 )

    def test_compare_calls_dictdiff_for_longest_iterable_wanted(self, purgemock, savemock, decidemock, diffmock):
        self.PrinterMock.get.return_value = [1]
        self.TestCls.compare( [1]*10 )
        self.assertEqual( diffmock.call_count, 10 )

    def test_compare_calls_saveDecide_for_longest_iterable_present_rules(self, purgemock, savemock, decidemock, diffmock):
        self.PrinterMock.get.return_value = [1] * 10
        self.TestCls.compare( [1] )
        self.assertEqual( savemock.call_count, 10 )

    def test_compare_calls_saveDecide_for_longest_iterable_wanted(self, purgemock, savemock, decidemock, diffmock):
        self.PrinterMock.get.return_value = [1]
        self.TestCls.compare( [1]*10 )
        self.assertEqual( savemock.call_count, 10 )

    def test_compare_calls_decide_for_longest_iterable_present_rules(self, purgemock, savemock, decidemock, diffmock):
        self.PrinterMock.get.return_value = [1] * 10
        self.TestCls.compare( [1] )
        self.assertEqual( decidemock.call_count, 10 )

    def test_compare_calls_decide_for_longest_iterable_wanted(self, purgemock, savemock, decidemock, diffmock):
        self.PrinterMock.get.return_value = [1]
        self.TestCls.compare( [1]*10 )
        self.assertEqual( decidemock.call_count, 10 )



@patch('menus.dictdiff')
class SingleTests(TestCase):

    def setUp(self):
        self.PrinterMock = MagicMock()
        self.wanted = MagicMock()
        self.TestCls = SingleMenu( printer=self.PrinterMock, keys=tuple(), exact=False )

    def test_returns_DEL_as_empty_tuple(self, diffmock):
        DEL, SET, ADD = self.TestCls.compare( self.wanted )
        self.assertEqual( DEL, tuple() )

    def test_returns_ADD__as_empty_tuple(self, diffmock):
        DEL, SET, ADD = self.TestCls.compare( self.wanted )
        self.assertEqual( ADD, tuple() )

    def test_calls_dictdiff_with_extracted_first_element(self, diffmock):
        self.PrinterMock.get.return_value = ('get_value', )
        self.TestCls.compare( self.wanted )
        diffmock.assert_called_once_with(wanted=self.wanted, present='get_value')

    def test_calls_printers_get_method(self, diffmock):
        self.TestCls.compare( self.wanted )
        self.PrinterMock.get.assert_called_once_with()

    def test_returns_non_empty_SET_as_tuple_if_difference(self, diffmock):
        diffmock.return_value = self.wanted
        DEL, SET, ADD = self.TestCls.compare( self.wanted )
        self.assertEqual( (self.wanted,), SET )

    def test_returns_empty_SET_as_tuple_if_no_difference(self, diffmock):
        diffmock.return_value = dict()
        DEL, SET, ADD = self.TestCls.compare( self.wanted )
        self.assertEqual( SET, tuple() )



@patch.object(GenericMenu, 'purge')
@patch.object(GenericMenu, 'decide')
@patch.object(GenericMenu, 'saveDecide')
@patch.object(WithKeyMenu, 'mkkvp')
@patch('menus.dictdiff')
class WithKey_compare_Tests(TestCase):

    def setUp(self):
        self.PrinterMock = MagicMock()
        self.wanted = ( MagicMock(), MagicMock() )
        self.TestCls = WithKeyMenu( printer=self.PrinterMock, keys=('name',), exact=True )

    def test_compare_calls_printers_get_method(self, diffmock, mkkvpmock, savemock, decidemock, purgemock):
        self.TestCls.compare(self.wanted)
        self.assertEqual( self.PrinterMock.get.call_count, 2 )

    def test_compare_calls_dictdiff(self, diffmock, mkkvpmock, savemock, decidemock, purgemock):
        self.TestCls.compare(self.wanted)
        self.assertEqual( diffmock.call_count, 2 )

    def test_compare_calls_purge(self, diffmock, mkkvpmock, savemock, decidemock, purgemock):
        self.TestCls.compare(self.wanted)
        purgemock.assert_called_once_with()

    def test_compare_calls_mkkvp(self, diffmock, mkkvpmock, savemock, decidemock, purgemock):
        self.TestCls.compare(self.wanted)
        self.assertEqual( mkkvpmock.call_count, 2 )

    def test_compare_calls_decide(self, diffmock, mkkvpmock, savemock, decidemock, purgemock):
        self.TestCls.compare(self.wanted)
        self.assertEqual( decidemock.call_count, 2 )

    def test_compare_calls_saveDecide(self, mkkvpmock, diffmock, savemock, decidemock, purgemock):
        self.TestCls.compare(self.wanted)
        self.assertEqual( savemock.call_count, 2 )

class WithKey_mkkvp_Tests(TestCase):

    def setUp(self):
        self.PrinterMock = MagicMock()
        self.wanted = ( MagicMock(), MagicMock() )
        self.TestCls = WithKeyMenu( printer=self.PrinterMock, keys=('name',), exact=True )

    def test_mkkvp_extracts_key_value_pair_when_keys_have_one_element(self):
        self.TestCls.keys = ('name',)
        kvp = self.TestCls.mkkvp( {'name':'some_name', 'ID':2} )
        self.assertEqual( {'name':'some_name'}, kvp )

    def test_mkkvp_extracts_key_value_pairs_when_keys_have_multiple_elements(self):
        self.TestCls.keys = ('name','address')
        kvp = self.TestCls.mkkvp( {'name':'some_name', 'address':'1.1.1.1', 'ID':2} )
        self.assertEqual( {'name':'some_name','address':'1.1.1.1'}, kvp )
