# -*- coding: UTF-8 -*-

from mock import MagicMock, patch
from unittest import TestCase

from mcm.configurators import CmdPathConfigurator, real_action, no_action, Configurator
from mcm.exceptions import ReadError
from mcm.librouteros.exc import ConnError


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



@patch('mcm.configurators.get_comparator')
@patch.object(CmdPathConfigurator, '__init__', return_value=None)
class Strategy_Factory_Tests(TestCase):

    def setUp(self):
        self.path, self.configurator = MagicMock(), MagicMock()

    def test_with_ensure_calls_init_with_appropriate_methods(self, initmock, cmpmock):
        CmdPathConfigurator.with_ensure(path=self.path, configurator=self.configurator)
        initmock.assert_called_once_with(path=self.path, comparator=cmpmock.return_value, configurator=self.configurator,
                addfunc=real_action, delfunc=no_action, setfunc=real_action)

    def test_with_exact_calls_init_with_appropriate_methods(self, initmock, cmpmock):
        CmdPathConfigurator.with_exact(path=self.path, configurator=self.configurator)
        initmock.assert_called_once_with(path=self.path, comparator=cmpmock.return_value, configurator=self.configurator,
                addfunc=real_action, delfunc=real_action, setfunc=real_action)



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



class Configurator_Tests(TestCase):

    def setUp(self):
        self.TestCls = Configurator(master=MagicMock(), slave=MagicMock())
        self.path = MagicMock()

    @patch.object(Configurator, 'getPathConfigurator')
    def test_run_calls_getPathConfigurator(self, pathcfgmock):
        self.TestCls.run(paths=(self.path,))
        pathcfgmock.assert_any_call(path=self.path)

    @patch.object(Configurator, 'getPathConfigurator')
    def test_run_calls_run(self, pathcfgmock):
        '''After calling getPathConfigurator, assert that its run() was called.'''
        self.TestCls.run(paths=(self.path,))
        pathcfgmock.return_value.run.assert_called_once_with()

    @patch.object(Configurator, 'getPathConfigurator')
    def test_run_catches_ReadError(self, pathcfgmock):
        pathcfgmock.return_value.run.side_effect = ReadError
        self.TestCls.run(paths=(self.path,))

    @patch.object(Configurator, 'getPathConfigurator')
    def test_run_catches_ConnError(self, pathcfgmock):
        pathcfgmock.return_value.run.side_effect = ConnError
        self.TestCls.run(paths=(self.path,))

    @patch.object(Configurator, 'getPathConfigurator')
    def test_run_breaks_loop_ConnError(self, pathcfgmock):
        """After first ConnError, break the configuration loop."""
        pathcfgmock.return_value.run.side_effect = ConnError
        self.TestCls.run(paths=(self.path,self.path))
        assert pathcfgmock.return_value.run.call_count == 1

    @patch.object(CmdPathConfigurator, 'with_ensure')
    def test_getPathConfigurator_calls_with_ensure(self, ensuremock):
        '''When strategy is ensure assert that with_ensure is called.'''
        self.path.strategy = 'ensure'
        self.TestCls.getPathConfigurator(path=self.path)
        ensuremock.assert_called_once_with(configurator=self.TestCls, path=self.path)

    @patch.object(CmdPathConfigurator, 'with_exact')
    def test_getPathConfigurator_calls_with_exact(self, exactmock):
        '''When strategy is exact assert that with_exact is called.'''
        self.path.strategy = 'exact'
        self.TestCls.getPathConfigurator(path=self.path)
        exactmock.assert_called_once_with(configurator=self.TestCls, path=self.path)

    @patch.object(Configurator, 'getPathConfigurator')
    def test_run_calls_master_close(self, pathcfgmock):
        '''After iterating over all paths close master.'''
        self.TestCls.run(paths=(self.path,))
        self.TestCls.master.close.assert_called_once_with()

    @patch.object(Configurator, 'getPathConfigurator')
    def test_run_calls_slave_close(self, pathcfgmock):
        '''After iterating over all paths close slave.'''
        self.TestCls.run(paths=(self.path,))
        self.TestCls.slave.close.assert_called_once_with()

