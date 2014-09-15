# -*- coding: UTF-8 -*-

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch
from unittest import TestCase

from repositories import UniqueKeyRepo, OrderedCmdRepo, SingleCmdRepo, get_repository, GenericRepo

class GenericRepo_Tests(TestCase):

    def setUp(self):
        self.TestCls = GenericRepo(class_type=MagicMock(), keys=MagicMock(), split_map=MagicMock())
        self.IODevice = MagicMock()
        self.Path = MagicMock()
        self.Data = MagicMock()
        self.DataElemMock = MagicMock()
        self.Data.__iter__.return_value = iter( [self.DataElemMock] )

    def test_read_calls_read_on_passed_device_instance(self):
        self.TestCls.read( self.IODevice, self.Path )
        self.IODevice.read.assert_called_once_with( path=self.Path )

    @patch.object(GenericRepo, 'assembleData')
    def test_read_calls_class_type(self, asseMock):
        self.TestCls.read( self.IODevice, self.Path )
        self.TestCls.class_type.assert_called_once_with(data=asseMock.return_value)

    @patch.object(GenericRepo, 'assembleData')
    def test_read_calls_assembleData(self, asseMock):
        data = self.IODevice.read.return_value = MagicMock()
        self.TestCls.read( device=self.IODevice, path=self.Path )
        asseMock.assert_called_once_with(data=data)

    @patch.object(GenericRepo, 'disassembleData')
    def test_write_calls_device_write(self, dissMock):
        self.TestCls.write( device=self.IODevice, data=self.Data, path=self.Path )
        self.IODevice.write.assert_called_once_with( data=dissMock.return_value, path=self.Path )

    @patch.object(GenericRepo, 'disassembleData')
    def test_write_calls_disassembleData(self, dissMock):
        self.TestCls.write( device=self.IODevice, data=self.Data, path=self.Path )
        dissMock.assert_called_once_with(data=self.Data)

    @patch('repositories.CmdPathElem')
    def test_assembleData_calls_CmdPathElem(self, elemmock):
        self.TestCls.assembleData(data=self.Data)
        elemmock.assert_any_call(data=self.DataElemMock, keys=self.TestCls.keys, split_map=self.TestCls.split_map)

    def test_disassemble_calls_iter_on_data(self):
        self.TestCls.disassembleData(data=self.Data)
        self.Data.__iter__.assert_called_once_with()



class UniqueKeyRepo_Tests(TestCase):

    def setUp(self):
        self.keys = MagicMock()
        self.TestCls = UniqueKeyRepo(class_type=MagicMock(), keys=self.keys, split_map=MagicMock())

    def test_after_init_keys_is_same_as_passed_argument(self):
        self.assertEqual(self.TestCls.keys, self.keys)



class SingleCmdRepo_Tests(TestCase):

    def setUp(self):
        self.TestCls = SingleCmdRepo(class_type=MagicMock(), keys=MagicMock(), split_map=MagicMock())

    def test_after_init_keys_is_tuple_regardless_of_passed_value(self):
        self.assertEqual(tuple(), self.TestCls.keys)



class OrderedCmdRepo_Tests(TestCase):

    def setUp(self):
        self.TestCls = OrderedCmdRepo(class_type=MagicMock(), keys=MagicMock(), split_map=MagicMock())

    def test_after_init_keys_is_tuple_regardless_of_passed_value(self):
        self.assertEqual(tuple(), self.TestCls.keys)



class Reposotory_Factory_Tests(TestCase):

    def setUp(self):
        self.keys = MagicMock()
        self.split_map = MagicMock()

    def test_get_repository_returns_SingleCmdRepo_instance_when_called_with_single(self):
        repo = get_repository(type='single', keys=None, split_map=None)
        self.assertIsInstance(repo, SingleCmdRepo)

    def test_get_repository_returns_OrderedCmdRepo_instance_when_called_with_ordered(self):
        repo = get_repository(type='ordered', keys=None, split_map=None)
        self.assertIsInstance(repo, OrderedCmdRepo)

    def test_get_repository_returns_UniqueCmdRepo_instance_when_called_with_uniquekey(self):
        repo = get_repository(type='uniquekey', keys=None, split_map=None)
        self.assertIsInstance(repo, UniqueKeyRepo)

    @patch('repositories.SingleElementCmdPath')
    @patch('repositories.SingleCmdRepo')
    def test_get_repository_instantiates_SingleCmdRepo_with_attributes_as_passed_in_function_call(self, repo, path):
        get_repository(type='single', keys=self.keys, split_map=self.split_map)
        repo.assert_called_once_with(class_type=path, keys=self.keys, split_map=self.split_map)

    @patch('repositories.UniqueKeyCmdPath')
    @patch('repositories.UniqueKeyRepo')
    def test_get_repository_instantiates_UniqieCmdRepo_with_attributes_as_passed_in_function_call(self, repo, path):
        get_repository(type='uniquekey', keys=self.keys, split_map=self.split_map)
        repo.assert_called_once_with(class_type=path, keys=self.keys, split_map=self.split_map)

    @patch('repositories.OrderedCmdPath')
    @patch('repositories.OrderedCmdRepo')
    def test_get_repository_instantiates_OrderedCmdRepo_with_attributes_as_passed_in_function_call(self, repo, path):
        get_repository(type='ordered', keys=self.keys, split_map=self.split_map)
        repo.assert_called_once_with(class_type=path, keys=self.keys, split_map=self.split_map)

