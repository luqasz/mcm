# -*- coding: UTF-8 -*-

try:
    from unittest.mock import MagicMock, patch, call
except ImportError:
    from mock import MagicMock, patch, call
from unittest import TestCase


from configurators import CmdPathConfigurator, real_action, no_action, getStrategyMethods, Configurator, mkCmdPathConfigurator


class CmdPathConfigurator_Tests(TestCase):

    def setUp(self):
        self.addfunc = MagicMock()
        self.delfunc = MagicMock()
        self.setfunc = MagicMock()
        self.TestCls = CmdPathConfigurator( path=MagicMock(), configurator=MagicMock(), comparator=MagicMock(), addfunc=self.addfunc, delfunc=self.delfunc, setfunc=self.setfunc )

    @patch.object(CmdPathConfigurator, 'applyData')
    @patch.object(CmdPathConfigurator, 'compareData')
    @patch.object(CmdPathConfigurator, 'readData')
    def test_run_calls_readData(self, readData_mock, compare_mock, apply_mock):
        self.TestCls.run()
        readData_mock.assert_called_once_with()

    @patch.object(CmdPathConfigurator, 'applyData')
    @patch.object(CmdPathConfigurator, 'compareData')
    @patch.object(CmdPathConfigurator, 'readData')
    def test_run_calls_compareData_with_data_from_readData(self, readData_mock, compare_mock, apply_mock):
        data = readData_mock.return_value = MagicMock()
        self.TestCls.run()
        compare_mock.assert_called_once_with(data)

    @patch.object(CmdPathConfigurator, 'applyData')
    @patch.object(CmdPathConfigurator, 'compareData')
    @patch.object(CmdPathConfigurator, 'readData')
    def test_run_calls_applyData_with_result_from_compareData(self, readData_mock, compare_mock, apply_mock):
        data = compare_mock.return_value = MagicMock()
        self.TestCls.run()
        apply_mock.assert_called_once_with(data=data)


    def test_compareData_calls_slaves_compare_with_master_data(self):
        master_data = MagicMock()
        slave_data = MagicMock()
        self.TestCls.compareData( (master_data, slave_data) )
        self.TestCls.comparator.compare.assert_called_once_with( wanted=master_data, present=slave_data )


    @patch.object(CmdPathConfigurator, 'extartActionData')
    def test_applyData_calls_extractActionData_with_data_and_action(self, extractmock):
        data_mock = MagicMock()
        self.TestCls.path.modord = ('ADD',)
        self.TestCls.applyData( data=data_mock )
        extractmock.assert_called_once_with( data=data_mock, action='ADD' )

    @patch.object(CmdPathConfigurator, 'extartActionData')
    def test_applyData_calls_addfunc_if_ADD_in_modord(self, extractmock):
        self.TestCls.path.modord = ('ADD',)
        self.TestCls.applyData( data=MagicMock() )
        self.addfunc.assert_called_once_with( self.TestCls, 'ADD', extractmock.return_value )

    @patch.object(CmdPathConfigurator, 'extartActionData')
    def test_applyData_does_not_call_addfunc_if_ADD_not_in_modord(self, extractmock):
        self.TestCls.path.modord = ()
        self.TestCls.applyData( data=MagicMock() )
        self.assertEqual( self.addfunc.call_count, 0 )

    @patch.object(CmdPathConfigurator, 'extartActionData')
    def test_applyData_calls_setfunc_if_SET_in_modord(self, extractmock):
        self.TestCls.path.modord = ('SET',)
        self.TestCls.applyData( data=MagicMock() )
        self.setfunc.assert_called_once_with( self.TestCls, 'SET', extractmock.return_value )

    @patch.object(CmdPathConfigurator, 'extartActionData')
    def test_applyData_does_not_call_setfunc_if_SET_not_in_modord(self, extractmock):
        self.TestCls.path.modord = ()
        self.TestCls.applyData( data=MagicMock() )
        self.assertEqual( self.setfunc.call_count, 0 )

    @patch.object(CmdPathConfigurator, 'extartActionData')
    def test_applyData_calls_delfunc_if_DEL_in_modord(self, extractmock):
        self.TestCls.path.modord = ('DEL',)
        self.TestCls.applyData( data=MagicMock() )
        self.delfunc.assert_called_once_with( self.TestCls, 'DEL', extractmock.return_value )

    @patch.object(CmdPathConfigurator, 'extartActionData')
    def test_applyData_does_not_call_delfunc_if_DEL_not_in_modord(self, extractmock):
        self.TestCls.path.modord = ()
        self.TestCls.applyData( data=MagicMock() )
        self.assertEqual( self.delfunc.call_count, 0 )


    def test_readData_calls_slave_read(self):
        self.TestCls.readData()
        self.TestCls.configurator.slave.read.assert_called_once_with(path=self.TestCls.path)


    def test_readData_calls_master_read(self):
        self.TestCls.readData()
        self.TestCls.configurator.master.read.assert_called_once_with(path=self.TestCls.path)


    def test_extractActionData_returns_ADD_data_when_requested(self):
        data = ADD, SET, DEL = ( MagicMock(), MagicMock(), MagicMock() )
        returned = self.TestCls.extartActionData(data=data, action='ADD')
        self.assertEqual(returned, ADD)

    def test_extractActionData_returns_SET_data_when_requested(self):
        data = ADD, SET, DEL = ( MagicMock(), MagicMock(), MagicMock() )
        returned = self.TestCls.extartActionData(data=data, action='SET')
        self.assertEqual(returned, SET)

    def test_extractActionData_returns_DEL_data_when_requested(self):
        data = ADD, SET, DEL = ( MagicMock(), MagicMock(), MagicMock() )
        returned = self.TestCls.extartActionData(data=data, action='DEL')
        self.assertEqual(returned, DEL)


class StrategyMethods_Tests(TestCase):

    def setUp(self):
        self.cls = MagicMock()
        self.data = MagicMock()

    def test_real_action_calls_slaves_write(self):
        real_action(self.cls, 'ADD', self.data)
        self.cls.configurator.slave.write.assert_called_once_with(data=self.data, path=self.cls.path, action='ADD')

    def test_no_action_does_not_call_masters_write(self):
        no_action(self.cls, 'ADD', self.data)
        self.assertEqual( self.cls.configurator.master.write.call_count, 0 )



class Strategy_Factory_Tests(TestCase):

    def setUp(self):
        self.exact = real_action, real_action, real_action
        self.ensure = real_action, no_action, real_action

    def test_exact_returns_valid_functions(self):
        returned = getStrategyMethods(strategy='exact')
        self.assertEqual( returned, self.exact )

    def test_ensure_returns_valid_functions(self):
        returned = getStrategyMethods(strategy='ensure')
        self.assertEqual( returned, self.ensure )


@patch('configurators.CmdPathConfigurator')
@patch('configurators.getStrategyMethods', return_value=('add', 'del', 'set'))
@patch('configurators.get_comparator')
class CmdPathConfigurator_factory_tests(TestCase):

    def setUp(self):
        self.Configurator = MagicMock()
        self.Path = MagicMock()

    def test_mkCmdPathConfigurator_calls_getStrategyMethods(self, comparator_mock, methods_mock, configurator_mock):
        mkCmdPathConfigurator(configurator=self.Configurator, path=self.Path)
        methods_mock.assert_called_once_with(strategy=self.Path.strategy)

    def test_mkCmdPathConfigurator_calls_get_comparator(self, comparator_mock, methods_mock, configurator_mock):
        mkCmdPathConfigurator(configurator=self.Configurator, path=self.Path)
        comparator_mock.assert_called_once_with(path=self.Path)

    def test_mkCmdPathConfigurator_calls_CmdPathConfigurator(self, comparator_mock, methods_mock, configurator_mock):
        mkCmdPathConfigurator(configurator=self.Configurator, path=self.Path)
        configurator_mock.assert_called_once_with(configurator=self.Configurator, comparator=comparator_mock.return_value, path=self.Path, addfunc='add', setfunc='set', delfunc='del')




class Configurator_Tests(TestCase):

    def setUp(self):
        self.TestCls = Configurator(master=MagicMock(), slave=MagicMock())

    @patch('configurators.mkCmdPathConfigurator')
    def test_run_calls_mkCmdPathConfigurator(self, mk_cmd_mock):
        self.TestCls.run(paths=(1,2))
        mk_cmd_mock.assert_any_call(configurator=self.TestCls, path=1)

    @patch('configurators.mkCmdPathConfigurator')
    def test_run_calls_CmdPathConfigurator_run(self, mk_cmd_mock):
        self.TestCls.run(paths=(1,2))
        mk_cmd_mock.return_value.run.assert_any_call()
