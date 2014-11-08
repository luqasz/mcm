# -*- coding: UTF-8 -*-

try:
    from unittest.mock import MagicMock, patch, call, PropertyMock
except ImportError:
    from mock import MagicMock, patch, call, PropertyMock
from unittest import TestCase


from iodevices import JsonFileConfig, RouterOsAPIDevice



class JsonFileConfig_Tests(TestCase):

    def setUp(self):
        self.TestCls = JsonFileConfig(file=MagicMock())

    def test_write_raises_NotImplemented(self):
        with self.assertRaises( NotImplementedError ):
            self.TestCls.write( data=MagicMock(), path=MagicMock() )



class RouterOsAPIDevice_Tests(TestCase):

    def setUp(self):
        self.ApiMock = MagicMock()
        self.TestCls = RouterOsAPIDevice(api=self.ApiMock)
        self.pathmock = MagicMock()
        type(self.pathmock).cmd = PropertyMock()
        self.datamock = MagicMock()

    def test_read_calls_api_run_method(self):
        self.TestCls.read(self.pathmock)
        self.ApiMock.run.assert_called_once_with(cmd=self.pathmock.cmd)

    def test_write_calls_api_run_method(self):
        self.TestCls.write(data=self.datamock, path=self.pathmock)
        self.ApiMock.run.assert_called_once_with(cmd=self.pathmock.cmd, args=self.datamock)

