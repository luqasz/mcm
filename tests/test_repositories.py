# -*- coding: UTF-8 -*-

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch
from unittest import TestCase

from repositories import UniqueKeyRepo, OrderedCmdRepo, SingleCmdRepo

class UniqueKeyRepo_Tests(TestCase):

    def setUp(self):
        self.TestCls = UniqueKeyRepo()
        self.IODevice = MagicMock()
        self.Path = MagicMock()
        self.Data = MagicMock()

    @patch('repositories.UniqueKeyCmdPath')
    def test_read_calls_read_on_passed_device_instance(self, Cmdpath):
        self.TestCls.read( self.IODevice, self.Path )
        self.IODevice.read.assert_called_once_with( self.Path )

    @patch('repositories.UniqueKeyCmdPath')
    def test_read_instantiates_UniqueCmdPath_with_read_content_from_device(self, Cmdpath):
        data = self.IODevice.read.return_value = MagicMock()
        self.TestCls.read( self.IODevice, self.Path )
        Cmdpath.assert_called_once_with( data )

    @patch('repositories.UniqueKeyCmdPath')
    def test_read_returns_UniqueCmdPath_instance(self, Cmdpath):
        Cmdpath.return_value = MagicMock()
        returned = self.TestCls.read( self.IODevice, self.Path )
        self.assertEqual( returned, Cmdpath.return_value )

    def test_write_calls_device_write(self):
        self.TestCls.write( self.IODevice, self.Data, self.Path )
        self.IODevice.write.assert_called_once_with( self.Data, self.Path )


class SingleCmdRepo_Tests(TestCase):

    def setUp(self):
        self.TestCls = SingleCmdRepo()
        self.IODevice = MagicMock()
        self.Path = MagicMock()
        self.Data = MagicMock()

    @patch('repositories.SingleElementCmdPath')
    def test_read_calls_read_on_passed_device_instance(self, Cmdpath):
        self.TestCls.read( self.IODevice, self.Path )
        self.IODevice.read.assert_called_once_with( self.Path )

    @patch('repositories.SingleElementCmdPath')
    def test_read_instantiates_SingleElementCmdPath_with_read_content_from_device(self, Cmdpath):
        data = self.IODevice.read.return_value = MagicMock()
        self.TestCls.read( self.IODevice, self.Path )
        Cmdpath.assert_called_once_with( data )

    @patch('repositories.SingleElementCmdPath')
    def test_read_returns_SingleElementCmdPath_instance(self, Cmdpath):
        Cmdpath.return_value = MagicMock()
        returned = self.TestCls.read( self.IODevice, self.Path )
        self.assertEqual( returned, Cmdpath.return_value )

    def test_write_calls_device_write(self):
        self.TestCls.write( self.IODevice, self.Data, self.Path )
        self.IODevice.write.assert_called_once_with( self.Data, self.Path )


class OrderedCmdRepo_Tests(TestCase):

    def setUp(self):
        self.TestCls = OrderedCmdRepo()
        self.IODevice = MagicMock()
        self.Path = MagicMock()
        self.Data = MagicMock()

    @patch('repositories.OrderedCmdPath')
    def test_read_calls_read_on_passed_device_instance(self, Cmdpath):
        self.TestCls.read( self.IODevice, self.Path )
        self.IODevice.read.assert_called_once_with( self.Path )

    @patch('repositories.OrderedCmdPath')
    def test_read_instantiates_OrderedCmdPath_with_read_content_from_device(self, Cmdpath):
        data = self.IODevice.read.return_value = MagicMock()
        self.TestCls.read( self.IODevice, self.Path )
        Cmdpath.assert_called_once_with( data )

    @patch('repositories.OrderedCmdPath')
    def test_read_returns_OrderedCmdPath_instance(self, Cmdpath):
        Cmdpath.return_value = MagicMock()
        returned = self.TestCls.read( self.IODevice, self.Path )
        self.assertEqual( returned, Cmdpath.return_value )

    def test_write_calls_device_write(self):
        self.TestCls.write( self.IODevice, self.Data, self.Path )
        self.IODevice.write.assert_called_once_with( self.Data, self.Path )

