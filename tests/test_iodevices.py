# -*- coding: UTF-8 -*-

from mock import MagicMock, patch
from inspect import ismethod
import pytest


from mcm.iodevices import RouterOsAPIDevice, StaticConfig, ReadOnlyRouterOS
from mcm.librouteros import TrapError, MultiTrapError
from mcm.exceptions import ReadError, WriteError


@pytest.fixture
def read_only_routeros():
    return ReadOnlyRouterOS(api=MagicMock())


class StaticConfig_Tests:

    def setup(self):
        data = [
                {'path': 'test_path', 'strategy': 'exact', 'rules': [{'key': 'value'}]}
                ]
        self.TestCls = StaticConfig(data=data)

    def test_read_returns_valid_rules(self):
        returned = self.TestCls.read(path='test_path')
        assert returned == [{'key': 'value'}]

    def test_has_close_method(self):
        assert ismethod(self.TestCls.close)


class Test_RouterOsAPIDevice:

    def setup(self):
        self.TestCls = RouterOsAPIDevice(api=MagicMock())
        self.pathmock = MagicMock()
        self.datamock = MagicMock()

    @patch.object(RouterOsAPIDevice, 'filter_dynamic')
    def test_read_calls_api(self, filter_mock):
        self.TestCls.read(self.pathmock)
        self.TestCls.api.assert_called_once_with(cmd=self.TestCls.api.joinPath.return_value)

    @pytest.mark.parametrize('exception', (TrapError, MultiTrapError))
    def test_read_raises_ReadError(self, exception):
        self.TestCls.api.side_effect = exception('message')
        with pytest.raises(ReadError) as error:
            self.TestCls.read(path=MagicMock())
        assert str(error.value) == 'message'

    @patch.object(RouterOsAPIDevice, 'filter_dynamic')
    def test_read_calls_joinPath(self, filter_mock):
        self.TestCls.read(self.pathmock)
        self.TestCls.api.joinPath.assert_called_once_with(self.pathmock, self.TestCls.actions['GET'])

    @patch.object(RouterOsAPIDevice, 'filter_dynamic')
    def test_read_calls_filter_dynamic(self, filter_mock):
        self.TestCls.read(self.pathmock)
        filter_mock.assert_called_once_with(self.TestCls.api.return_value)

    @pytest.mark.parametrize('action', ('ADD', 'SET', 'DEL'))
    def test_write_calls_joinPath(self, action):
        setattr(self.TestCls, action, MagicMock())
        self.TestCls.write(path=self.pathmock, action=action, data=None)
        self.TestCls.api.joinPath.assert_called_once_with(self.pathmock, self.TestCls.actions[action])

    @pytest.mark.parametrize('action', ('ADD', 'SET', 'DEL'))
    def test_write_calls_action_method(self, action):
        setattr(self.TestCls, action, MagicMock())
        self.TestCls.write(data='data', path=self.pathmock, action=action)
        getattr(self.TestCls, action).assert_called_once_with(command=self.TestCls.api.joinPath.return_value, data='data')

    def test_DEL_calls_api_only_with_ID(self):
        data = {'.id': '*1', 'address': '1.1.1.1/24'}
        self.TestCls.DEL(command='/ip/address/remove', data=data)
        self.TestCls.api.assert_called_once_with(cmd='/ip/address/remove', **{'.id': '*1'})

    @pytest.mark.parametrize('action', ('ADD', 'SET'))
    def test_action_methods_call_api(self, action):
        data, command = MagicMock(), MagicMock()
        getattr(self.TestCls, action)(command=command, data=data)
        self.TestCls.api.assert_called_once_with(cmd=command, **data)

    @pytest.mark.parametrize('exception', (TrapError, MultiTrapError))
    @pytest.mark.parametrize('action', ('ADD', 'SET', 'DEL'))
    def test_write_raises_WriteError(self, exception, action):
        setattr(self.TestCls, action, MagicMock(side_effect=exception('message')))
        with pytest.raises(WriteError) as error:
            self.TestCls.write(path=MagicMock(), action=action, data=MagicMock())
        assert str(error.value) == 'message'

    def test_close_calls_api_close(self):
        self.TestCls.close()
        self.TestCls.api.close.assert_called_once_with()


@pytest.mark.parametrize("action", ('ADD', 'SET', 'DEL'))
def test_DryRunRouterOS_write_passes(read_only_routeros, action):
    """Assert that DEL SET ADD methods are not called."""
    setattr(read_only_routeros, action, MagicMock())
    read_only_routeros.write(path='path', action=action, data=None)
    assert getattr(read_only_routeros, action).call_count == 0


@pytest.mark.parametrize("response,expected", (
    (({'dynamic': False}, {'dynamic': True}), ({'dynamic': False}, )),
    (({'dynamic': True}, ), ()),
    ))
def test_filter_dynamic(response, expected):
    assert RouterOsAPIDevice.filter_dynamic(response) == expected
