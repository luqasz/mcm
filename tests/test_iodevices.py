# -*- coding: UTF-8 -*-

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch
from unittest import TestCase
from inspect import ismethod


from iodevices import RouterOsAPIDevice, StaticConfig
from librouteros import CmdError
from exceptions import ReadError, WriteError



class StaticConfig_Tests(TestCase):

    def setUp(self):
        data = [
                {'path':'test_path', 'strategy':'exact', 'rules':[ {'key':'value'} ]}
                ]
        self.TestCls = StaticConfig(data=data)

    def test_read_returns_valid_rules(self):
        returned = self.TestCls.read(path='test_path')
        self.assertEqual(returned, [{'key':'value'}])

    def test_has_close_method(self):
        self.assertTrue(ismethod(self.TestCls.close))



class RouterOsAPIDevice_Tests(TestCase):

    def setUp(self):
        self.TestCls = RouterOsAPIDevice(api=MagicMock())
        self.pathmock = MagicMock()
        self.datamock = MagicMock()

    @patch.object(RouterOsAPIDevice, 'filter_dynamic')
    @patch.object(RouterOsAPIDevice, 'cmd_action_join')
    def test_read_calls_api_run_method(self, joinmock, filter_mock):
        self.TestCls.read(self.pathmock)
        self.TestCls.api.run.assert_called_once_with(cmd=joinmock.return_value)

    @patch.object(RouterOsAPIDevice, 'cmd_action_join')
    def test_read_raises_ReadError(self, joinmock):
        self.TestCls.api.run.side_effect = CmdError
        with self.assertRaises(ReadError):
            self.TestCls.read(path=MagicMock())

    @patch.object(RouterOsAPIDevice, 'filter_dynamic')
    @patch.object(RouterOsAPIDevice, 'cmd_action_join')
    def test_read_calls_cmd_action_join(self, joinmock, filter_mock):
        self.TestCls.read(self.pathmock)
        joinmock.assert_called_once_with(path=self.pathmock, action='GET')

    @patch.object(RouterOsAPIDevice, 'filter_dynamic')
    @patch.object(RouterOsAPIDevice, 'cmd_action_join')
    def test_read_calls_filter_dynamic(self, joinmock, filter_mock):
        self.TestCls.read(self.pathmock)
        filter_mock.assert_called_once_with(self.TestCls.api.run.return_value)

    @patch.object(RouterOsAPIDevice, 'ADD')
    @patch.object(RouterOsAPIDevice, 'cmd_action_join')
    def test_write_calls_cmd_action_join(self, joinmock, addmock):
        self.TestCls.write(path=self.pathmock, action='ADD', data=None)
        joinmock.assert_called_once_with(path=self.pathmock, action='ADD')


    @patch.object(RouterOsAPIDevice, 'DEL')
    @patch.object(RouterOsAPIDevice, 'cmd_action_join')
    def test_write_calls_DEL_when_cmd_is_DEL(self, joinmock, delmock):
        self.TestCls.write(data='data', path=self.pathmock, action='DEL')
        delmock.assert_called_once_with(command=joinmock.return_value, data='data')

    @patch.object(RouterOsAPIDevice, 'ADD')
    @patch.object(RouterOsAPIDevice, 'cmd_action_join')
    def test_write_calls_ADD_when_cmd_is_ADD(self, joinmock, addmock):
        self.TestCls.write(data='data', path=self.pathmock, action='ADD')
        addmock.assert_called_once_with(command=joinmock.return_value, data='data')

    @patch.object(RouterOsAPIDevice, 'SET')
    @patch.object(RouterOsAPIDevice, 'cmd_action_join')
    def test_write_calls_SET_when_cmd_is_SET(self, joinmock, setmock):
        self.TestCls.write(data='data', path=self.pathmock, action='SET')
        setmock.assert_called_once_with(command=joinmock.return_value, data='data')


    def test_DEL_calls_api_run_only_with_ID(self):
        data = {'.id':'*1', 'address':'1.1.1.1/24'}
        self.TestCls.DEL(command='/ip/address/remove', data=data)
        self.TestCls.api.run.assert_called_once_with(cmd='/ip/address/remove', args={'.id':'*1'})

    def test_DEL_raises_WriteError(self):
        self.TestCls.api.run.side_effect = CmdError
        with self.assertRaises(WriteError):
            self.TestCls.DEL(command=MagicMock(), data=MagicMock())

    def test_ADD_calls_api_run(self):
        data, command = MagicMock(), MagicMock()
        self.TestCls.ADD(command=command, data=data)
        self.TestCls.api.run.assert_called_once_with(cmd=command, args=data)

    def test_ADD_raises_WriteError(self):
        self.TestCls.api.run.side_effect = CmdError
        with self.assertRaises(WriteError):
            self.TestCls.ADD(command=MagicMock(), data=MagicMock())

    def test_SET_calls_api_run(self):
        data, command = MagicMock(), MagicMock()
        self.TestCls.SET(command=command, data=data)
        self.TestCls.api.run.assert_called_once_with(cmd=command, args=data)

    def test_SET_raises_WriteError(self):
        self.TestCls.api.run.side_effect = CmdError
        with self.assertRaises(WriteError):
            self.TestCls.SET(command=MagicMock(), data=MagicMock())

    def test_close_calls_api_close(self):
        self.TestCls.close()
        self.TestCls.api.close.assert_called_once_with()



class cmd_action_join_Tests(TestCase):

    def test_returns_appended_remove_string_without_ending_forward_slash(self):
        cmd = RouterOsAPIDevice.cmd_action_join('/ip/address', action='DEL')
        self.assertEqual( cmd, '/ip/address/remove' )

    def test__returns_appended_add_string_without_ending_forward_slash(self):
        cmd = RouterOsAPIDevice.cmd_action_join('/ip/address', action='ADD')
        self.assertEqual( cmd, '/ip/address/add' )

    def test__returns_appended_set_string_without_ending_forward_slash(self):
        cmd = RouterOsAPIDevice.cmd_action_join('/ip/address', action='SET')
        self.assertEqual( cmd, '/ip/address/set' )

    def test__returns_appended_getall_string_without_ending_forward_slash(self):
        cmd = RouterOsAPIDevice.cmd_action_join('/ip/address', action='GET')
        self.assertEqual( cmd, '/ip/address/getall' )


class filter_dynamic_Tests(TestCase):

    def setUp(self):
        self.dynamic = dict(dynamic=True)
        self.static = dict(dynamic=False)
        self.data = ( self.dynamic, self.static )

    def test_returns_only_static(self):
        result = RouterOsAPIDevice.filter_dynamic(self.data)
        self.assertEqual(result, (self.static,))

    def test_returns_tuple(self):
        result = RouterOsAPIDevice.filter_dynamic(self.data)
        self.assertIs(type(result), tuple)

