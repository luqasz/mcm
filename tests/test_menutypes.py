# -*- coding: UTF-8 -*-

try:
    from unittest.mock import MagicMock, patch, call
except ImportError:
    from mock import MagicMock, patch, call
from unittest import TestCase




class ModuleMocks(TestCase):

    @classmethod
    def setUpClass(cls):
        librouteros_mock = MagicMock()
        cls.mp = patch.dict('sys.modules', {'librouteros.extras':librouteros_mock})
        cls.mp.start()

    @classmethod
    def tearDownClass(cls):
        cls.mp.stop()



class SingleElement(ModuleMocks):

    def setUp(self):
        self.PrinterMock = MagicMock()
        self.wanted = MagicMock()

        from menutypes import Single
        self.TestCls = Single( self.PrinterMock )

    @patch('menutypes.dictdiff')
    def test_returns_DEL_as_empty_tuple(self, diffmock):
        DEL, SET, ADD = self.TestCls.compare( self.wanted )
        self.assertEqual( DEL, tuple() )

    @patch('menutypes.dictdiff')
    def test_returns_ADD__as_empty_tuple(self, diffmock):
        DEL, SET, ADD = self.TestCls.compare( self.wanted )
        self.assertEqual( ADD, tuple() )

    @patch('menutypes.dictdiff')
    def test_calls_dictdiff(self, diffmock):
        self.TestCls.compare( self.wanted )
        self.assertEqual( diffmock.call_count, 1 )

    @patch('menutypes.dictdiff')
    def test_calls_printers_get_method(self, diffmock):
        self.TestCls.compare( self.wanted )
        self.PrinterMock.get.assert_called_once_with()

    @patch('menutypes.dictdiff')
    def test_returns_non_empty_SET_as_tuple_if_difference(self, diffmock):
        diffmock.return_value = self.wanted
        DEL, SET, ADD = self.TestCls.compare( self.wanted )
        self.assertEqual( (self.wanted,), SET )

    @patch('menutypes.dictdiff')
    def test_returns_empty_SET_as_tuple_if_no_difference(self, diffmock):
        diffmock.return_value = dict()
        DEL, SET, ADD = self.TestCls.compare( self.wanted )
        self.assertEqual( SET, tuple() )







class UnorderedWithKey(ModuleMocks):

    def setUp(self):
        self.PrinterMock = MagicMock()
        self.wanted = ( MagicMock(), MagicMock() )

        from menutypes import SimpleKey
        self.TestCls = SimpleKey( self.PrinterMock, key='name', exact=True )

    @patch('menutypes.SimpleKey.decide')
    @patch('menutypes.SimpleKey.purge')
    @patch('menutypes.dictdiff')
    def test_compare_calls_printers_get_method(self, diffmock, purgemock, decidemock):
        self.TestCls.compare(self.wanted)
        self.assertEqual( self.PrinterMock.get.call_count, 2 )

    @patch('menutypes.SimpleKey.decide')
    @patch('menutypes.SimpleKey.purge')
    @patch('menutypes.dictdiff')
    def test_compare_calls_dictdiff(self, diffmock, purgemock, decidemock):
        self.TestCls.compare(self.wanted)
        self.assertEqual( diffmock.call_count, 2 )

    @patch('menutypes.SimpleKey.decide')
    @patch('menutypes.SimpleKey.purge')
    @patch('menutypes.dictdiff')
    def test_compare_calls_purge(self, diffmock, purgemock, decidemock):
        self.TestCls.compare(self.wanted)
        purgemock.assert_called_once_with(self.wanted)

    @patch('menutypes.SimpleKey.decide')
    @patch('menutypes.SimpleKey.purge')
    @patch('menutypes.dictdiff')
    def test_compare_calls_decide(self, diffmock, purgemock, decidemock):
        self.TestCls.compare(self.wanted)
        self.assertEqual( decidemock.call_count, 2 )

    def test_decide_appends_to_SET_with_ID_if_non_empty_present(self):
        present = {'ID':1}
        diff = {'name':1}
        self.TestCls.decide(diff, present)
        diff.update(present)
        self.assertEqual( [ diff ], self.TestCls.SET )

    def test_decide_appends_to_ADD_if_empty_present(self):
        diff = {'name':1}
        present = {}
        self.TestCls.decide(diff, present)
        self.assertEqual( [ diff ], self.TestCls.ADD )

    def test_purge_calls_printers_notIn_method_if_exact_is_True(self):
        self.TestCls.purge( self.wanted )
        self.assertEqual( self.PrinterMock.notIn.call_count, 1 )

    def test_purge_appends_to_DEL_if_exact_is_True(self):
        self.PrinterMock.notIn.return_value = [ 1,2,3 ]
        self.TestCls.purge( self.wanted )
        self.assertEqual( self.TestCls.DEL, [1,2,3] )

    def test_purge_leaves_DEL_empty_if_exact_is_False(self):
        self.TestCls.exact = False
        self.TestCls.purge( self.wanted )
        self.assertEqual( self.TestCls.DEL, [] )

    def test_purge_does_not_call_printers_notIn_method_if_exact_is_False(self):
        self.TestCls.exact = False
        self.TestCls.purge( self.wanted )
        self.assertEqual( self.PrinterMock.notIn.call_count , 0 )





class CompositeKeyTests(ModuleMocks):

    def setUp(self):
        self.PrinterMock = MagicMock()
        self.wanted = ( {'list':'blacklist','address':'1.1.1.1','dynamic':False}, {'list':'blacklist','address':'2.2.2.2','dynamic':False} )

        from menutypes import CompositeKey
        self.TestCls = CompositeKey( self.PrinterMock, keys=('list','address'), exact=True )


    @patch('menutypes.CompositeKey.decide')
    @patch('menutypes.CompositeKey.purge')
    @patch('menutypes.dictdiff')
    def test_compare_calls_printers_get_method_for_every_rule(self, diffmock, purgemock, decidemock):
        self.TestCls.compare(self.wanted)
        self.assertEqual( self.PrinterMock.get.call_count, 2 )

    @patch('menutypes.CompositeKey.decide')
    @patch('menutypes.CompositeKey.purge')
    @patch('menutypes.dictdiff')
    def test_compare_calls_dictdiff(self, diffmock, purgemock, decidemock):
        self.TestCls.compare(self.wanted)
        self.assertEqual( diffmock.call_count, 2 )

    @patch('menutypes.CompositeKey.decide')
    @patch('menutypes.CompositeKey.purge')
    @patch('menutypes.dictdiff')
    def test_compare_calls_purge(self, diffmock, purgemock, decidemock):
        self.TestCls.compare(self.wanted)
        purgemock.assert_called_once_with(self.wanted)

    @patch('menutypes.CompositeKey.decide')
    @patch('menutypes.CompositeKey.purge')
    @patch('menutypes.dictdiff')
    def test_compare_calls_decide(self, diffmock, purgemock, decidemock):
        self.TestCls.compare(self.wanted)
        self.assertEqual( decidemock.call_count, 2 )

    def test_decide_appends_to_SET_with_ID_if_non_empty_present(self):
        present = {'ID':1}
        diff = {'name':1}
        self.TestCls.decide(diff, present)
        diff.update(present)
        self.assertEqual( [ diff ], self.TestCls.SET )

    def test_decide_appends_to_ADD_if_empty_present(self):
        diff = {'name':1}
        present = {}
        self.TestCls.decide(diff, present)
        self.assertEqual( [ diff ], self.TestCls.ADD )

    def test_purge_calls_printers_notIn_method_if_exact_is_True(self):
        self.TestCls.purge( self.wanted )
        self.assertEqual( self.PrinterMock.notIn.call_count, 1 )

    def test_purge_appends_to_DEL_if_exact_is_True(self):
        self.PrinterMock.notIn.return_value = [ 1,2,3 ]
        self.TestCls.purge( self.wanted )
        self.assertEqual( self.TestCls.DEL, [1,2,3] )

    def test_purge_leaves_DEL_empty_if_exact_is_False(self):
        self.TestCls.exact = False
        self.TestCls.purge( self.wanted )
        self.assertEqual( self.TestCls.DEL, [] )

    def test_purge_does_not_call_printers_notIn_method_if_exact_is_False(self):
        self.TestCls.exact = False
        self.TestCls.purge( self.wanted )
        self.assertEqual( self.PrinterMock.notIn.call_count , 0 )
