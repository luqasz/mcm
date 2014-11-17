# -*- coding: UTF-8 -*-

try:
    from unittest.mock import MagicMock, patch, call, PropertyMock
except ImportError:
    from mock import MagicMock, patch, call, PropertyMock
from unittest import TestCase


from configurators import CmdPathConfigurator, realADD, realDEL, realSET, dummyDEL, dummySET, dummyADD, getStrategyMethods


class CmdPathConfigurator_Tests(TestCase):

    def setUp(self):
        self.addfunc = MagicMock()
        self.delfunc = MagicMock()
        self.setfunc = MagicMock()
        self.master = MagicMock()
        self.slave = MagicMock()
        self.repository = MagicMock()
        self.path = MagicMock()
        self.TestCls = CmdPathConfigurator( repository=self.repository, master=self.master,
        slave=self.slave, addfunc=self.addfunc, delfunc=self.delfunc, setfunc=self.setfunc)

    @patch.object(CmdPathConfigurator, 'applyData')
    @patch.object(CmdPathConfigurator, 'compareData')
    @patch.object(CmdPathConfigurator, 'readData')
    def test_run_calls_readData_with_path(self, readData_mock, compare_mock, apply_mock):
        readData_mock.return_value = MagicMock(), MagicMock()
        self.TestCls.run( path=self.path, modord=tuple() )
        readData_mock.assert_called_once_with( self.path )

    @patch.object(CmdPathConfigurator, 'applyData')
    @patch.object(CmdPathConfigurator, 'compareData')
    @patch.object(CmdPathConfigurator, 'readData')
    def test_run_calls_compareData_with_data_from_readData(self, readData_mock, compare_mock, apply_mock):
        data = readData_mock.return_value = MagicMock()
        self.TestCls.run( path=self.path, modord=tuple() )
        compare_mock.assert_called_once_with(data)

    @patch.object(CmdPathConfigurator, 'applyData')
    @patch.object(CmdPathConfigurator, 'compareData')
    @patch.object(CmdPathConfigurator, 'readData')
    def test_run_calls_applyData(self, readData_mock, compare_mock, apply_mock):
        data = compare_mock.return_value = MagicMock()
        mod_mock = MagicMock()
        self.TestCls.run( path=self.path, modord=mod_mock )
        apply_mock.assert_called_once_with(path=self.path, data=data, modord=mod_mock)


    def test_compareData_calls_compare_on_slave_data_with_passed_master_data(self):
        master_data = MagicMock()
        slave_data = MagicMock()
        self.TestCls.compareData( (master_data, slave_data) )
        slave_data.compare.assert_called_once_with( master_data )


    @patch.object(CmdPathConfigurator, 'extartActionData')
    def test_applyData_calls_extartActionData_three_times_if_modord_has_three_actions(self, extractmock ):
        self.TestCls.applyData( path=self.path, modord=('ADD','SET','DEL'), data=MagicMock() )
        self.assertEqual( extractmock.call_count, 3 )

    @patch.object(CmdPathConfigurator, 'extartActionData')
    def test_applyData_calls_addfunc_if_ADD_in_modord(self, extractmock):
        self.TestCls.applyData( path=self.path, modord=('ADD',), data=MagicMock() )
        self.addfunc.assert_called_once_with( self.TestCls, extractmock.return_value, self.path )

    @patch.object(CmdPathConfigurator, 'extartActionData')
    def test_applyData_does_not_call_addfunc_if_ADD_not_in_modord(self, extractmock):
        self.TestCls.applyData( path=self.path, modord=('DEL','SET'), data=MagicMock() )
        self.assertEqual( self.addfunc.call_count, 0 )

    @patch.object(CmdPathConfigurator, 'extartActionData')
    def test_applyData_calls_setfunc_if_SET_in_modord(self, extractmock):
        self.TestCls.applyData( path=self.path, modord=('SET',), data=MagicMock() )
        self.setfunc.assert_called_once_with( self.TestCls, extractmock.return_value, self.path  )

    @patch.object(CmdPathConfigurator, 'extartActionData')
    def test_applyData_does_not_call_setfunc_if_SET_not_in_modord(self, extractmock):
        self.TestCls.applyData( path=self.path, modord=('DEL','ADD'), data=MagicMock() )
        self.assertEqual( self.setfunc.call_count, 0 )

    @patch.object(CmdPathConfigurator, 'extartActionData')
    def test_applyData_calls_delfunc_if_DEL_in_modord(self, extractmock):
        self.TestCls.applyData( path=self.path, modord=('DEL',), data=MagicMock() )
        self.delfunc.assert_called_once_with( self.TestCls, extractmock.return_value, self.path  )

    @patch.object(CmdPathConfigurator, 'extartActionData')
    def test_applyData_does_not_call_delfunc_if_DEL_not_in_modord(self, extractmock):
        self.TestCls.applyData( path=self.path, modord=('ADD','SET'), data=MagicMock() )
        self.assertEqual( self.delfunc.call_count, 0 )

    @patch.object(CmdPathConfigurator, 'extartActionData')
    def test_applyData_calls_modification_functions_in_passed_order(self, extractmock):
        manager = MagicMock()
        manager.DEL = self.delfunc
        manager.SET = self.setfunc
        manager.ADD = self.addfunc
        self.TestCls.applyData( path=self.path, modord=('ADD','SET','DEL'), data=MagicMock() )
        expected = [call.ADD(self.TestCls, extractmock.return_value, self.path ),
                call.SET(self.TestCls, extractmock.return_value, self.path ),
                call.DEL(self.TestCls, extractmock.return_value, self.path )]
        manager.assert_has_calls(expected)


    def test_readSlave_calls_respository_read_with_slave_device_and_path(self):
        self.TestCls.readSlave(self.path)
        self.repository.read.assert_called_once_with(device=self.slave, path=self.path)

    def test_readSlave_sets_path_cmd_to_getall(self):
        self.TestCls.readSlave(self.path)
        self.assertEqual(self.path.cmd, self.path.getall)


    def test_readMaster_calls_respository_read_with_master_device_and_path(self):
        self.TestCls.readMaster(self.path)
        self.repository.read.assert_called_once_with(device=self.master, path=self.path)

    def test_readMaster_sets_path_cmd_to_getall(self):
        self.TestCls.readMaster(self.path)
        self.assertEqual(self.path.cmd, self.path.getall)


    def test_extractActionData_returns_ADD_data_when_requested(self):
        data = ADD, SET, DEL = ( MagicMock(), MagicMock(), MagicMock() )
        returned = CmdPathConfigurator.extartActionData(data=data, action='ADD')
        self.assertEqual(returned, ADD)

    def test_extractActionData_returns_SET_data_when_requested(self):
        data = ADD, SET, DEL = ( MagicMock(), MagicMock(), MagicMock() )
        returned = CmdPathConfigurator.extartActionData(data=data, action='SET')
        self.assertEqual(returned, SET)

    def test_extractActionData_returns_DEL_data_when_requested(self):
        data = ADD, SET, DEL = ( MagicMock(), MagicMock(), MagicMock() )
        returned = CmdPathConfigurator.extartActionData(data=data, action='DEL')
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

    def test_realADD_sets_path_cmd_to_add(self):
        realADD(self.obj, self.data, self.path)
        self.assertEqual(self.path.cmd, self.path.add)

    def test_realDEL_calls_repository_write_with_data_row(self):
        realDEL(self.obj, self.data, self.path)
        self.obj.repository.write.assert_any_call(device=self.obj.slave, data=(self.datarow,), path=self.path)

    def test_realDEL_sets_path_cmd_to_remove(self):
        realDEL(self.obj, self.data, self.path)
        self.assertEqual(self.path.cmd, self.path.remove)

    def test_realSET_calls_repository_write_with_data_row(self):
        realSET(self.obj, self.data, self.path)
        self.obj.repository.write.assert_any_call(device=self.obj.slave, data=(self.datarow,), path=self.path)

    def test_realSET_sets_path_cmd_to_set(self):
        realSET(self.obj, self.data, self.path)
        self.assertEqual(self.path.cmd, self.path.set)



class Strategy_Factory_Tests(TestCase):

    def setUp(self):
        self.dry_run = {'addfunc':dummyADD, 'delfunc':dummyDEL, 'setfunc':dummySET}
        self.exact = {'addfunc':realADD, 'delfunc':realDEL, 'setfunc':realSET}
        self.ensure = {'addfunc':realADD, 'delfunc':dummyDEL, 'setfunc':realSET}

    def test_getStrategyMethods_returns_all_dummy_functions_when_called_with_dry_run_strategy(self):
        returned = getStrategyMethods(strategy='dry_run')
        self.assertEqual( returned, self.dry_run )

    def test_getStrategyMethods_returns_all_real_functions_when_called_with_exact_strategy(self):
        returned = getStrategyMethods(strategy='exact')
        self.assertEqual( returned, self.exact )

    def test_getStrategyMethods_returns_all_real_functions_except_delfunc_when_called_with_ensure_strategy(self):
        returned = getStrategyMethods(strategy='ensure')
        self.assertEqual( returned, self.ensure )

