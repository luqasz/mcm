# -*- coding: UTF-8 -*-

from mock import MagicMock, patch
import pytest

from mcm.adapters import MasterAdapter, SlaveAdapter
from mcm.exceptions import WriteError


@pytest.fixture
def master_adapter():
    return MasterAdapter(device=MagicMock())


@pytest.fixture
def slave_adapter():
    return SlaveAdapter(device=MagicMock())


@pytest.fixture
def path():
    return MagicMock()


@pytest.fixture
def data_row():
    return MagicMock(name='data_element')


@pytest.fixture
def data_set(data_row):
    return (data_row,)


def test_MasterAdapter_calls_devices_read(master_adapter, path):
    master_adapter.assemble_data = MagicMock()
    master_adapter.read(path=path)
    master_adapter.device.read.assert_called_once_with(path=path.absolute)


def test_MasterAdapter_calls_assemble_data(master_adapter, path):
    master_adapter.assemble_data = MagicMock()
    master_adapter.read(path=path)
    master_adapter.assemble_data.assert_called_once_with(data=master_adapter.device.read.return_value)


@pytest.mark.parametrize("adapter", (master_adapter(), slave_adapter()))
def test_adapters_device_close(adapter):
    adapter.close()
    adapter.device.close.assert_called_once_with()


@patch('mcm.adapters.CmdPathRow')
def test_assemble_data_calls_CmdPathRow(rowmock, master_adapter, data_set, data_row):
    master_adapter.assemble_data(data=data_set)
    rowmock.assert_any_call(data_row)


@patch('mcm.adapters.CmdPathRow')
def test_assemble_data_returns_tuple(rowmock, master_adapter, data_set, data_row):
    result = master_adapter.assemble_data(data=data_set)
    assert type(result) == tuple


def test_SlaveAdapter_write_calls_device_write(slave_adapter, data_set, path, data_row):
    slave_adapter.write(path=path, action='ADD', data=data_set)
    slave_adapter.device.write.assert_any_call(path=path.absolute, action='ADD', data=data_row)


def test_SlaveAdapter_write_catches_WriteError(slave_adapter, data_set, path):
    slave_adapter.device.side_effect = WriteError
    slave_adapter.write(path=path, action='ADD', data=data_set)
