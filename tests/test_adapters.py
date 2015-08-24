# -*- coding: UTF-8 -*-

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch
from unittest import TestCase

from adapters import MasterAdapter, SlaveAdapter
from exceptions import WriteError



class MasterAdapter_Tests(TestCase):

    def setUp(self):
        self.element = MagicMock()
        self.data = [self.element]
        self.TestCls = MasterAdapter(device=MagicMock())
        self.path = MagicMock()

    @patch.object(MasterAdapter, 'assemble_data')
    def test_read_calls_device_read(self, assemblemock):
        self.TestCls.read(path=self.path)
        self.TestCls.device.read.assert_called_once_with(path=self.path.absolute)

    @patch.object(MasterAdapter, 'assemble_data')
    def test_read_calls_assemble_data(self, assemblemock):
        self.TestCls.read(path=self.path)
        assemblemock.assert_called_once_with(data=self.TestCls.device.read.return_value)

    @patch('adapters.CmdPathRow')
    def test_assemble_data_calls_CmdPathRow(self, rowmock):
        self.TestCls.assemble_data(data=self.data)
        rowmock.assert_any_call(data=self.element)

    @patch('adapters.CmdPathRow')
    def test_assemble_data_returns_tuple(self,rowmock):
        returned = self.TestCls.assemble_data(data=self.data)
        self.assertIs(type(returned), tuple)

    def test_close_calls_device_close(self):
        self.TestCls.close()
        self.TestCls.device.close.assert_called_once_with()


class SlaveAdapter_Tests(TestCase):

    def setUp(self):
        self.TestCls = SlaveAdapter(device=MagicMock())
        self.path = MagicMock()
        self.row = MagicMock()
        self.row.data = MagicMock()
        self.data = (self.row, )

    def test_write_calls_device_write_with_absolute_path_and_rows_data(self):
        self.TestCls.write(path=self.path, action=None, data=self.data)
        self.TestCls.device.write.assert_any_call(path=self.path.absolute, action=None, data=self.row.data)

    def test_Write_catches_WriteError(self):
        self.TestCls.device.write.side_effect = WriteError
        try:
            self.TestCls.write(path=self.path, action=None, data=self.data)
        except:
            self.fail('Unexpected exception raised!')
