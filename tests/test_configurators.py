# -*- coding: UTF-8 -*-

try:
    from unittest.mock import MagicMock, patch, call, PropertyMock
except ImportError:
    from mock import MagicMock, patch, call, PropertyMock
from unittest import TestCase


from configurators import GenericConfigurator, NonQueriedConfigurator, DryRunConfigurator
from exc import ConfigRunError


class GenericConfigurator_applyMenu_Tests(TestCase):

    def setUp(self):
        self.TestCls = GenericConfigurator( None, None )
        self.TestCls.ADD = MagicMock()
        self.TestCls.DEL = MagicMock()
        self.TestCls.SET = MagicMock()
        self.rules = MagicMock()
        self.MenuType = MagicMock()
        self.MenuType.compare.return_value = ('DEL', 'SET', 'ADD')
        self.modord = ('SET', 'ADD')
        self.PathMock = MagicMock()

    def test_calls_compare(self):
        self.TestCls.applyMenu( rules=self.rules, menu_type=self.MenuType, modord=self.modord, path=self.PathMock )
        self.MenuType.compare.assert_called_once_with( self.rules )

    def test_does_not_call_ADD_SET_DEL_when_Menu_type_compare_method_raises_ConfigRunError(self):
        self.MenuType.compare.side_effect = ConfigRunError()
        self.TestCls.applyMenu( rules=self.rules, menu_type=self.MenuType, modord=self.modord, path=self.PathMock )
        self.assertEqual(0, self.TestCls.SET.call_count)
        self.assertEqual(0, self.TestCls.ADD.call_count)
        self.assertEqual(0, self.TestCls.DEL.call_count)

    def test_calls_ADD_if_specified_in_modord(self):
        self.modord = ('ADD', )
        self.TestCls.applyMenu( rules=self.rules, menu_type=self.MenuType, modord=self.modord, path=self.PathMock )
        self.TestCls.ADD.assert_called_once_with('ADD', self.PathMock)

    def test_calls_SET_if_specified_in_modord(self):
        self.modord = ('SET', )
        self.TestCls.applyMenu( rules=self.rules, menu_type=self.MenuType, modord=self.modord, path=self.PathMock )
        self.TestCls.SET.assert_called_once_with('SET', self.PathMock)

    def test_does_not_call_DEL_if_not_listed_in_modord(self):
        self.modord = ('SET', 'ADD')
        self.TestCls.applyMenu( rules=self.rules, menu_type=self.MenuType, modord=self.modord, path=self.PathMock )
        self.assertEqual(0, self.TestCls.DEL.call_count)




class NonQueriedConfigurator_SET_Tests(TestCase):

    def setUp(self):
        self.ApiMock = MagicMock()
        self.PathMock = MagicMock()
        self.Setmock = PropertyMock( return_value='set' )
        type(self.PathMock).set = self.Setmock
        self.TestCls = NonQueriedConfigurator( self.ApiMock, None )

    def test_calls_api_run_for_every_element_in_rules(self):
        self.TestCls.SET( rules=[1]*3, path=self.PathMock )
        self.assertEqual( self.ApiMock.run.call_count, 3 )

    def test_acceses_set_attribute(self):
        self.TestCls.SET( rules=[1], path=self.PathMock )
        self.Setmock.assert_called_once_with()

    def test_for_every_rule_calls_api_run_with_rule_as_argument(self):
        self.TestCls.SET( rules=[1]*2, path=self.PathMock )
        self.assertEqual( self.ApiMock.run.call_args_list, [call('set', 1)]*2 )


class NonQueriedConfigurator_DEL_Tests(TestCase):

    def setUp(self):
        self.ApiMock = MagicMock()
        self.PathMock = MagicMock()
        self.RemoveAttrMock = PropertyMock( return_value='del' )
        type(self.PathMock).remove = self.RemoveAttrMock
        self.TestCls = NonQueriedConfigurator( self.ApiMock, None )

    def test_calls_api_run_for_every_element_in_rules(self):
        self.TestCls.DEL( rules=[1]*3, path=self.PathMock )
        self.assertEqual( self.ApiMock.run.call_count, 3 )

    def test_acceses_del_attribute(self):
        self.TestCls.DEL( rules=[1], path=self.PathMock )
        self.RemoveAttrMock.assert_called_once_with()

    def test_for_every_rule_calls_api_run_with_rule_as_argument(self):
        self.TestCls.DEL( rules=[1]*2, path=self.PathMock )
        self.assertEqual( self.ApiMock.run.call_args_list, [call('del', 1)]*2 )


class NonQueriedConfigurator_ADD_Tests(TestCase):

    def setUp(self):
        self.ApiMock = MagicMock()
        self.PathMock = MagicMock()
        self.AddAttrMock = PropertyMock( return_value='add' )
        type(self.PathMock).add = self.AddAttrMock
        self.TestCls = NonQueriedConfigurator( self.ApiMock, None )

    def test_calls_api_run_for_every_element_in_rules(self):
        self.TestCls.ADD( rules=[1]*3, path=self.PathMock )
        self.assertEqual( self.ApiMock.run.call_count, 3 )

    def test_acceses_add_attribute(self):
        self.TestCls.ADD( rules=[1], path=self.PathMock )
        self.AddAttrMock.assert_called_once_with()

    def test_for_every_rule_calls_api_run_with_rule_as_argument(self):
        self.TestCls.ADD( rules=[1]*2, path=self.PathMock )
        self.assertEqual( self.ApiMock.run.call_args_list, [call('add', 1)]*2 )



class DryRunConfigurator_Tests(TestCase):

    def setUp(self):
        self.logmock = MagicMock()
        self.apimock = MagicMock()
        self.TestCls = DryRunConfigurator( self.apimock, self.logmock )
        self.rules = ({'address':'x.x.x.x','disabled':False}, {'address':'y.y.y.y','disabled':True})
        self.pathmock = MagicMock()

    def test_ADD_does_not_call_api_run_method(self):
        self.TestCls.ADD( rules=self.rules, path=self.pathmock )
        self.assertEqual( self.apimock.run.call_count, 0 )

    def test_SET_does_not_call_api_run_method(self):
        self.TestCls.SET( rules=self.rules, path=self.pathmock )
        self.assertEqual( self.apimock.run.call_count, 0 )

    def test_DEL_does_not_call_api_run_method(self):
        self.TestCls.DEL( rules=self.rules, path=self.pathmock )
        self.assertEqual( self.apimock.run.call_count, 0 )
