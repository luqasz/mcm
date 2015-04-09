# -*- coding: UTF-8 -*-

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch
from unittest import TestCase

from adapters import MasterAdapter, SlaveAdapter



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


class SlaveAdapter_Tests(TestCase):

    def setUp(self):
        self.TestCls = SlaveAdapter(device=MagicMock())
        self.path = MagicMock()
        self.elem1 = MagicMock()
        self.elem2 = MagicMock()
        self.elem1.data = 1
        self.elem2.data = 2

    def test_disassemble_data_extracts_data_attribute(self):
        returned = self.TestCls.disassemble_data(data=(self.elem1,self.elem2))
        self.assertEqual(returned, (1,2))

    def test_disassemble_data_returns_tuple(self):
        returned = self.TestCls.disassemble_data(data=(self.elem1,self.elem2))
        self.assertIs(type(returned), tuple)

    @patch.object(SlaveAdapter, 'disassemble_data')
    def test_write_calls_disassemble_data(self, disassemblemock):
        self.TestCls.write(path=None, action=None, data=(self.elem1,))
        disassemblemock.assert_called_once_with(data=(self.elem1,))

    @patch.object(SlaveAdapter, 'disassemble_data')
    def test_write_calls_device_write_with_absolute_path(self, disassemblemock):
        disassemblemock.return_value = (self.elem1,)
        self.TestCls.write(path=self.path, action=None, data=None)
        self.TestCls.device.write.assert_called_once_with(path=self.path.absolute, action=None, data=self.elem1)
