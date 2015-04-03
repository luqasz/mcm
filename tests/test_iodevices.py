# -*- coding: UTF-8 -*-

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch
from unittest import TestCase


from iodevices import RouterOsAPIDevice, cmd_action_join, filter_dynamic




class RouterOsAPIDevice_Tests(TestCase):

    def setUp(self):
        self.TestCls = RouterOsAPIDevice(api=MagicMock())
        self.pathmock = MagicMock()
        self.datamock = MagicMock()

    @patch('iodevices.filter_dynamic')
    @patch('iodevices.cmd_action_join')
    def test_read_calls_api_run_method(self, joinmock, filter_mock):
        self.TestCls.read(self.pathmock)
        self.TestCls.api.run.assert_called_once_with(cmd=joinmock.return_value)

    @patch('iodevices.filter_dynamic')
    @patch('iodevices.cmd_action_join')
    def test_read_calls_cmd_action_join(self, joinmock, filter_mock):
        self.TestCls.read(self.pathmock)
        joinmock.assert_called_once_with(path=self.pathmock, action='GET')

    @patch('iodevices.filter_dynamic')
    @patch('iodevices.cmd_action_join')
    def test_read_calls_filter_dynamic(self, joinmock, filter_mock):
        self.TestCls.read(self.pathmock)
        filter_mock.assert_called_once_with(self.TestCls.api.run.return_value)

    @patch('iodevices.cmd_action_join')
    def test_write_calls_cmd_action_join(self, joinmock):
        self.TestCls.write(path=self.pathmock, cmd='cmd', data=None)
        joinmock.assert_called_once_with(path=self.pathmock, action='cmd')

    @patch('iodevices.cmd_action_join')
    def test_write_calls_api_run_method(self, joinmock):
        self.TestCls.write(data='data', path=self.pathmock.absolute, cmd='cmd')
        self.TestCls.api.run.assert_called_once_with(cmd=joinmock.return_value, args='data')



class cmd_action_join_Tests(TestCase):

    def test_returns_appended_remove_string_without_ending_forward_slash(self):
        cmd = cmd_action_join('/ip/address', action='DEL')
        self.assertEqual( cmd, '/ip/address/remove' )

    def test__returns_appended_add_string_without_ending_forward_slash(self):
        cmd = cmd_action_join('/ip/address', action='ADD')
        self.assertEqual( cmd, '/ip/address/add' )

    def test__returns_appended_set_string_without_ending_forward_slash(self):
        cmd = cmd_action_join('/ip/address', action='SET')
        self.assertEqual( cmd, '/ip/address/set' )

    def test__returns_appended_getall_string_without_ending_forward_slash(self):
        cmd = cmd_action_join('/ip/address', action='GET')
        self.assertEqual( cmd, '/ip/address/getall' )


class filter_dynamic_Tests(TestCase):

    def setUp(self):
        self.dynamic = dict(dynamic=True)
        self.static = dict(dynamic=False)
        self.data = ( self.dynamic, self.static )

    def test_returns_only_static(self):
        result = filter_dynamic(self.data)
        self.assertTrue(result, (self.static,))

    def test_returns_tuple(self):
        result = filter_dynamic(self.data)
        self.assertIs(type(result), tuple)

