# -*- coding: UTF-8 -*-

try:
    from unittest.mock import MagicMock, patch, PropertyMock
except ImportError:
    from mock import MagicMock, patch, PropertyMock
from unittest import TestCase

from adapters import assemble_data, disassemble_data



class AssembleData_Tests(TestCase):

    def setUp(self):
        self.data = MagicMock()
        self.element = MagicMock()
        self.data.__iter__.return_value = (self.element,)

    @patch('adapters.CmdPathRow')
    def test_calls_CmdPathRow(self, cmd):
        assemble_data(data=self.data)
        cmd.assert_any_call(data=self.element)

    @patch('adapters.CmdPathRow')
    def test_returns_tuple(self,cmdrow):
        returned = assemble_data(data=self.data)
        self.assertIs(type(returned), tuple)


class DisassembleData_Tests(TestCase):

    def setUp(self):
        self.elem1 = MagicMock()
        self.elem2 = MagicMock()
        self.elem1.data = 1
        self.elem2.data = 2

    def test_extracts_data_attribute_when_multiple_element_data_is_passed(self):
        returned = disassemble_data(data=(self.elem1,self.elem2))
        self.assertEqual(returned, (1,2))

    def test_returns_tuple(self):
        returned = disassemble_data(data=(self.elem1,self.elem2))
        self.assertIs(type(returned), tuple)
