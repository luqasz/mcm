# -*- coding: UTF-8 -*-

try:
    from unittest.mock import MagicMock, patch, call, PropertyMock
except ImportError:
    from mock import MagicMock, patch, call, PropertyMock
from unittest import TestCase


from configurators import CmdPathConfigurator, realADD, realDEL, realSET, dummyDEL, dummySET, dummyADD
from exc import ConfigRunError


class CmdPathConfigurator_Tests(TestCase):

    def setUp(self):
        self.addfunc = MagicMock()
        self.delfunc = MagicMock()
        self.setfunc = MagicMock()
        self.master = MagicMock()
        self.slave = MagicMock()
        self.repository = MagicMock()
        map = { self.master:MagicMock(), self.slave:MagicMock() }
        self.repository.read.side_effect =  lambda *args, **kwargs: map[kwargs['device']]
        self.master_data = map[self.master]
        self.slave_data = map[self.slave]
        self.path = MagicMock()
        self.TestCls = CmdPathConfigurator( repository=self.repository, master=self.master,
                slave=self.slave, addfunc=self.addfunc, delfunc=self.delfunc, setfunc=self.setfunc)

    @patch.object(CmdPathConfigurator, 'extartActionData')
    def test_run_calls_repository_read_with_master_device(self, extractmock):
        self.TestCls.run( path=self.path, modord=tuple() )
        self.repository.read.assert_any_call(device=self.master, path=self.path)

    @patch.object(CmdPathConfigurator, 'extartActionData')
    def test_run_calls_repository_read_with_slave_device(self, extractmock):
        self.TestCls.run( path=self.path, modord=tuple())
        self.repository.read.assert_any_call(device=self.slave, path=self.path)

    @patch.object(CmdPathConfigurator, 'extartActionData')
    def test_run_calls_compare_on_slave_data_with_passed_master_data(self, extractmock):
        self.TestCls.run( path=self.path, modord=tuple() )
        self.slave_data.compare.assert_called_once_with( self.master_data )

    @patch.object(CmdPathConfigurator, 'extartActionData')
    def test_run_calls_extartActionData_three_time_if_modord_has_three_actions(self, extractmock):
        self.TestCls.run( path=self.path, modord=('ADD','SET','DEL') )
        self.assertEqual( extractmock.call_count, 3 )

    @patch.object(CmdPathConfigurator, 'extartActionData')
    def test_run_calls_addfunc_if_ADD_in_modord(self, extractmock):
        self.TestCls.run( path=self.path, modord=('ADD',) )
        self.addfunc.assert_called_once_with( self.TestCls, extractmock.return_value )

    @patch.object(CmdPathConfigurator, 'extartActionData')
    def test_run_does_not_call_addfunc_if_ADD_not_in_modord(self, extractmock):
        self.TestCls.run( path=self.path, modord=('DEL','SET') )
        self.assertEqual( self.addfunc.call_count, 0 )

    @patch.object(CmdPathConfigurator, 'extartActionData')
    def test_run_calls_setfunc_if_SET_in_modord(self, extractmock):
        self.TestCls.run( path=self.path, modord=('SET',) )
        self.setfunc.assert_called_once_with( self.TestCls, extractmock.return_value )

    @patch.object(CmdPathConfigurator, 'extartActionData')
    def test_run_does_not_call_setfunc_if_SET_not_in_modord(self, extractmock):
        self.TestCls.run( path=self.path, modord=('DEL','ADD') )
        self.assertEqual( self.setfunc.call_count, 0 )

    @patch.object(CmdPathConfigurator, 'extartActionData')
    def test_run_calls_delfunc_if_DEL_in_modord(self, extractmock):
        self.TestCls.run( path=self.path, modord=('DEL',) )
        self.delfunc.assert_called_once_with( self.TestCls, extractmock.return_value )

    @patch.object(CmdPathConfigurator, 'extartActionData')
    def test_run_does_not_call_delfunc_if_DEL_not_in_modord(self, extractmock):
        self.TestCls.run( path=self.path, modord=('ADD','SET') )
        self.assertEqual( self.delfunc.call_count, 0 )

    @patch.object(CmdPathConfigurator, 'extartActionData')
    def test_run_calls_modification_functions_in_passed_order(self, extractmock):
        manager = MagicMock()
        manager.DEL = self.delfunc
        manager.SET = self.setfunc
        manager.ADD = self.addfunc
        self.TestCls.run( path=self.path, modord=('ADD','SET','DEL') )
        expected = [call.ADD(self.TestCls, extractmock.return_value),
                call.SET(self.TestCls, extractmock.return_value),
                call.DEL(self.TestCls, extractmock.return_value)]
        manager.assert_has_calls(expected)

    def test_extractActionData_returns_ADD_data_when_requested(self):
        data = ADD, SET, DEL = ( MagicMock(), MagicMock(), MagicMock() )
        returned = CmdPathConfigurator.extartActionData(data=data, elem='ADD')
        self.assertEqual(returned, ADD)

    def test_extractActionData_returns_SET_data_when_requested(self):
        data = ADD, SET, DEL = ( MagicMock(), MagicMock(), MagicMock() )
        returned = CmdPathConfigurator.extartActionData(data=data, elem='SET')
        self.assertEqual(returned, SET)

    def test_extractActionData_returns_DEL_data_when_requested(self):
        data = ADD, SET, DEL = ( MagicMock(), MagicMock(), MagicMock() )
        returned = CmdPathConfigurator.extartActionData(data=data, elem='DEL')
        self.assertEqual(returned, DEL)


class ModificationFunctions_Tests(TestCase):

    def setUp(self):
        self.obj = MagicMock()
        self.datarow = MagicMock()
        self.data = MagicMock()
        self.data.__iter__.return_value = iter( [self.datarow] )
        self.path = MagicMock()

    def test_dummyDEL_does_not_call_repository_write(self):
        dummyDEL(self.obj, self.data, self.path)
        self.assertEqual(self.obj.repository.write.call_count, 0)

    def test_dummySET_does_not_call_repository_write(self):
        dummySET(self.obj, self.data, self.path)
        self.assertEqual(self.obj.repository.write.call_count, 0)

    def test_dummyADD_does_not_call_repository_write(self):
        dummyADD(self.obj, self.data, self.path)
        self.assertEqual(self.obj.repository.write.call_count, 0)

    def test_dummyADD_iterates_over_passed_data(self):
        dummyADD(self.obj, self.data, self.path)
        self.data.__iter__.assert_called_once_with()

    def test_dummyDEL_iterates_over_passed_data(self):
        dummyDEL(self.obj, self.data, self.path)
        self.data.__iter__.assert_called_once_with()

    def test_dummySET_iterates_over_passed_data(self):
        dummySET(self.obj, self.data, self.path)
        self.data.__iter__.assert_called_once_with()

    def test_realADD_iterates_over_passed_data(self):
        realADD(self.obj, self.data, self.path)
        self.data.__iter__.assert_called_once_with()

    def test_realDEL_iterates_over_passed_data(self):
        realDEL(self.obj, self.data, self.path)
        self.data.__iter__.assert_called_once_with()

    def test_realSET_iterates_over_passed_data(self):
        realSET(self.obj, self.data, self.path)
        self.data.__iter__.assert_called_once_with()

    def test_realADD_calls_repository_write_with_data_row(self):
        realADD(self.obj, self.data, self.path)
        self.obj.repository.write.assert_any_call(device=self.obj.slave, data=(self.datarow,), path=self.path)
