# -*- coding: UTF-8 -*-

from mock import MagicMock
from inspect import ismethod
import pytest


from mcm.iodevices import RW_RouterOs, StaticConfig, RO_RouterOs
from mcm.librouteros import TrapError, MultiTrapError
from mcm.exceptions import ReadError, WriteError


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


class Test_RO_RouterOs:

    def setup(self):
        self.TestCls = RO_RouterOs(api=MagicMock())
        self.pathmock = MagicMock()
        self.datamock = MagicMock()

    def test_read_calls_api(self):
        self.TestCls.read(self.pathmock)
        self.TestCls.api.assert_called_once_with(cmd=self.TestCls.api.joinPath.return_value)

    @pytest.mark.parametrize('exception', (TrapError, MultiTrapError))
    def test_read_raises_ReadError(self, exception):
        self.TestCls.api.side_effect = exception('message')
        with pytest.raises(ReadError) as error:
            self.TestCls.read(path=MagicMock())
        assert str(error.value) == 'message'

    def test_read_calls_joinPath(self):
        self.TestCls.read(self.pathmock)
        self.TestCls.api.joinPath.assert_called_once_with(self.pathmock, self.TestCls.actions['GET'])

    @pytest.mark.parametrize("action", ('ADD', 'SET', 'DEL'))
    def test_write_passes(self, action):
        """Assert that DEL SET ADD methods are not called."""
        setattr(self.TestCls, action, MagicMock())
        self.TestCls.write(path='path', action=action, data=None)
        assert getattr(self.TestCls, action).call_count == 0

    @pytest.mark.parametrize("response,expected", (
        (({'dynamic': False}, {'dynamic': True}), ({'dynamic': False}, )),
        (({'dynamic': True}, ), ()),
        ))
    def test_read_filters_dynamic(self, response, expected):
        self.TestCls.api.return_value = response
        assert self.TestCls.read(path=MagicMock()) == expected

    def test_close_calls_api_close(self):
        self.TestCls.close()
        self.TestCls.api.close.assert_called_once_with()


class Test_RW_RouterOs:

    def setup(self):
        self.TestCls = RW_RouterOs(api=MagicMock())
        self.pathmock = MagicMock()
        self.datamock = MagicMock()

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
