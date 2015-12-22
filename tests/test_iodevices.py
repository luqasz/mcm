# -*- coding: UTF-8 -*-

from mock import MagicMock, patch
from unittest import TestCase
from inspect import ismethod
import pytest


from mcm.iodevices import RouterOsAPIDevice, StaticConfig, ReadOnlyRouterOS
from mcm.librouteros import TrapError
from mcm.exceptions import ReadError, WriteError


@pytest.fixture
def read_only_routeros():
    return ReadOnlyRouterOS(api=MagicMock())


class StaticConfig_Tests:

    def setup(self):
        data = [
                {'path':'test_path', 'strategy':'exact', 'rules':[ {'key':'value'} ]}
                ]
        self.TestCls = StaticConfig(data=data)

    def test_read_returns_valid_rules(self):
        returned = self.TestCls.read(path='test_path')
        assert returned == [{'key':'value'}]

    def test_has_close_method(self):
        assert ismethod(self.TestCls.close)



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
        self.TestCls.api.run.side_effect = TrapError('message')
        with pytest.raises(ReadError):
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
        self.TestCls.api.run.side_effect = TrapError('message')
        with self.assertRaises(WriteError):
            self.TestCls.DEL(command=MagicMock(), data=MagicMock())

    def test_ADD_calls_api_run(self):
        data, command = MagicMock(), MagicMock()
        self.TestCls.ADD(command=command, data=data)
        self.TestCls.api.run.assert_called_once_with(cmd=command, args=data)

    def test_ADD_raises_WriteError(self):
        self.TestCls.api.run.side_effect = TrapError('message')
        with self.assertRaises(WriteError):
            self.TestCls.ADD(command=MagicMock(), data=MagicMock())

    def test_SET_calls_api_run(self):
        data, command = MagicMock(), MagicMock()
        self.TestCls.SET(command=command, data=data)
        self.TestCls.api.run.assert_called_once_with(cmd=command, args=data)

    def test_SET_raises_WriteError(self):
        self.TestCls.api.run.side_effect = TrapError('message')
        with self.assertRaises(WriteError):
            self.TestCls.SET(command=MagicMock(), data=MagicMock())

    def test_close_calls_api_close(self):
        self.TestCls.close()
        self.TestCls.api.close.assert_called_once_with()


@pytest.mark.parametrize("action", ('ADD', 'SET', 'DEL'))
def test_DryRunRouterOS_write_passes(read_only_routeros, action):
    """Assert that DEL SET ADD methods are not called."""
    setattr(read_only_routeros, action, MagicMock())
    read_only_routeros.write(path='path', action=action, data=None)
    assert getattr(read_only_routeros, action).call_count == 0



@pytest.mark.parametrize("path,action,expected",(
    ('/ip/address','DEL','/ip/address/remove'),
    ('/ip/address','ADD','/ip/address/add'),
    ('/ip/address','SET','/ip/address/set'),
    ('/ip/address','GET','/ip/address/getall'),
    ))
def test_cmd_action_join(path,action,expected):
    assert RouterOsAPIDevice.cmd_action_join(path=path,action=action) == expected


@pytest.mark.parametrize("response,expected",(
    ( ({'dynamic':False},{'dynamic':True}), ({'dynamic':False},) ),
    ( ({'dynamic':True},), () ),
    ))
def test_filter_dynamic(response,expected):
    assert RouterOsAPIDevice.filter_dynamic(response) == expected


