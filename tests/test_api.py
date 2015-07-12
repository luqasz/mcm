# -*- coding: UTF-8 -*-

import unittest
try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch

from librouteros.api import Api
from librouteros.exc import CmdError, ConnError, LibError
from librouteros.connections import ReaderWriter



@patch( 'librouteros.api.parsresp' )
@patch( 'librouteros.api.mksnt' )
@patch( 'librouteros.api.trapCheck' )
@patch( 'librouteros.api.raiseIfFatal' )
@patch.object( Api, '_readDone' )
@patch.object( Api, 'close' )
class RunMethod(unittest.TestCase):


    def setUp(self):

        rwo = MagicMock( spec = ReaderWriter )
        self.api = Api( rwo )


    def test_calls_mksnt(self, close_mock, read_mock, raise_mock, trap_mock, mksnt_mock, parsresp_mock):
        self.api.run( 'some level' )
        mksnt_mock.assert_called_once_with( dict() )

    def test_calls_write_sentence_with_combined_tuple(self, close_mock, read_mock, raise_mock, trap_mock, mksnt_mock, parsresp_mock):
        lvl = '/ip/address'
        retval = ('=key=value',)
        mksnt_mock.return_value = ( retval )
        self.api.run( lvl, 'some args' )
        self.api.rwo.writeSnt.assert_called_once_with( (lvl,) + retval )

    def test_calls_readdone(self, close_mock, read_mock, raise_mock, trap_mock, mksnt_mock, parsresp_mock):
        self.api.run( 'some string' )
        read_mock.assert_called_once_with()

    def test_calls_trapCheck(self, close_mock, read_mock, raise_mock, trap_mock, mksnt_mock, parsresp_mock):
        self.api._readDone.return_value = ( 'some read sentence' )
        self.api.run( 'some level' )
        trap_mock.assert_called_once_with( 'some read sentence' )

    def test_calls_parsresp(self, close_mock, read_mock, raise_mock, trap_mock, mksnt_mock, parsresp_mock):
        self.api._readDone.return_value = 'read sentence'
        self.api.run( 'some level' )
        parsresp_mock.assert_called_once_with( 'read sentence' )

    def test_checks_for_fatal_condition(self, close_mock, read_mock, raise_mock, trap_mock, mksnt_mock, parsresp_mock):
        self.api._readDone.return_value = ( 'some read sentence' )
        self.api.run( 'some level' )
        raise_mock.assert_called_once_with( 'some read sentence' )

    def test_raises_CmdError_if_trap_in_sentence(self, close_mock, read_mock, raise_mock, trap_mock, mksnt_mock, parsresp_mock):
        trap_mock.side_effect = CmdError()
        self.assertRaises( CmdError, self.api.run, ( 'some level' ) )

    def test_raises_ConnError_if_fatal_in_sentence(self, close_mock, read_mock, raise_mock, trap_mock, mksnt_mock, parsresp_mock):
        raise_mock.side_effect = ConnError()
        self.assertRaises( ConnError, self.api.run, ( 'some level' ) )



class ReadLoop(unittest.TestCase):


    def setUp(self):
        rwo = MagicMock( spec = ReaderWriter )
        self.api = Api( rwo )
        self.api.close = MagicMock()

    def test_returns_response_if_done_at_the_end_of_response(self):
        response = (('1','2'),('!done',))
        self.api.rwo.readSnt.side_effect = response
        self.assertEqual( self.api._readDone(), response )

    def test_returns_response_if_done_at_the_begining_of_sentence(self):
        response = (('!done', '1','2'),)
        self.api.rwo.readSnt.side_effect = response
        self.assertEqual( self.api._readDone(), response )

    def test_returns_response_if_done_at_the_end_of_sentence(self):
        response = (('1','2','!done'),)
        self.api.rwo.readSnt.side_effect = response
        self.assertEqual( self.api._readDone(), response )



class ClosingConnecton(unittest.TestCase):


    def setUp(self):
        rwo = MagicMock( spec = ReaderWriter )
        self.api = Api( rwo )

    def test_calls_write_sentence(self):
        self.api.close()
        self.api.rwo.writeSnt.assert_called_once_with( ('/quit',) )

    def test_calls_read_sentence(self):
        self.api.close()
        self.api.rwo.readSnt.assert_called_once_with()

    def test_calls_reader_writers_close_method(self):
        self.api.close()
        self.api.rwo.close.assert_called_once_with()

    def test_calls_reader_writers_close_method_even_if_write_raises_LibError(self):
        self.api.rwo.writeSnt.side_effect = LibError()
        self.api.close()
        self.api.rwo.close.assert_called_once_with()

    def test_calls_reader_writers_close_method_even_if_read_raises_LibError(self):
        self.api.rwo.readSnt.side_effect = LibError()
        self.api.close()
        self.api.rwo.close.assert_called_once_with()



class TimeoutManipulations(unittest.TestCase):


    def setUp(self):
        self.rwo = MagicMock()
        self.api = Api( self.rwo )

    def test_getting_timeout_value(self):
        self.api.timeout
        self.rwo.sock.gettimeout.assert_called_once

    def test_setting_timeout_0_raises_ValueError(self):
        with self.assertRaises(ValueError):
            self.api.timeout = 0

    def test_setting_timeout_lower_than_0_raises_ValueError(self):
        with self.assertRaises(ValueError):
            self.api.timeout = -1

    def test_calls_setting_timeout(self):
        self.api.timeout = 20
        self.rwo.sock.settimeout.assert_called_once_with(20)

