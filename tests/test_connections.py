# -*- coding: UTF-8 -*-

import unittest
from socket import SHUT_RDWR, error as SOCKET_ERROR, timeout as SOCKET_TIMEOUT, socket
try:
    from unittest.mock import MagicMock, call, patch
except ImportError:
    from mock import MagicMock, call, patch

import librouteros.connections as conn
from librouteros.exc import ConnError


class LengthEncoding(unittest.TestCase):


    def test_encodes_length_less_than_128( self ):
        self.assertEqual( conn.enclen( 127 ), b'\x7f' )

    def test_encodes_length_less_than_16384( self ):
        self.assertEqual( conn.enclen( 130 ), b'\x80\x82' )

    def test_encodes_length_less_than_2097152( self ):
        self.assertEqual( conn.enclen( 2097140 ), b'\xdf\xff\xf4' )

    def test_encodes_length_less_than_268435456( self ):
        self.assertEqual( conn.enclen( 268435440 ), b'\xef\xff\xff\xf0' )

    def test_raises_ConnError_if_lenghth_is_too_big( self ):
        '''Raises ConnError if length >= 268435456'''
        self.assertRaises( ConnError, conn.enclen, 268435456 )



class LengthDecoding(unittest.TestCase):


    def test_decodes_0_length( self ):
        self.assertEqual( conn.declen( b'\x00' ), 0 )

    def test_decodes_length_less_than_128( self ):
        self.assertEqual( conn.declen( b'\x7f' ), 127 )

    def test_decodes_length_less_than_16384( self ):
        self.assertEqual( conn.declen( b'\x80\x82' ), 130 )

    def test_decodes_length_less_than_2097152( self ):
        self.assertEqual( conn.declen( b'\xdf\xff\xf4' ), 2097140 )

    def test_decodes_length_less_than_268435456( self ):
        self.assertEqual( conn.declen( b'\xef\xff\xff\xf0'  ), 268435440 )

    def test_raises_ConnError_if_bytes_is_too_big( self ):
        '''Raises ConnError if length > 4 bytes'''
        self.assertRaises( ConnError, conn.declen, b'\xff\xff\xff\xff\xff' )



class GetLengths(unittest.TestCase):


    def setUp(self):
        patcher = patch('librouteros.connections.declen')
        self.dec_len_mock = patcher.start()
        self.addCleanup(patcher.stop)

        self.rwo = conn.ReaderWriter( None, None )
        self.rwo.readSock = MagicMock()

    def test_calls_declen(self):
        self.rwo.readSock.side_effect = [b'\x7f', b'']
        self.rwo.getLen()
        self.dec_len_mock.assert_called_once_with( b'\x7f' )

    def test_raises_if_first_byte_if_greater_than_239( self ):
        self.rwo.readSock.return_value = b'\xf0'
        self.assertRaises( ConnError, self.rwo.getLen )

    def test_calls_read_socket_less_than_128( self ):
        self.rwo.readSock.side_effect = [b'\x7f', b'']
        self.rwo.getLen()
        expected_calls = [ call(1), call(0) ]
        self.assertEqual( self.rwo.readSock.mock_calls, expected_calls )

    def test_calls_read_socket_less_than_16384( self ):
        self.rwo.readSock.side_effect = [ b'\x80', b'\x82' ]
        self.rwo.getLen()
        expected_calls = [ call(1), call(1) ]
        self.assertEqual( self.rwo.readSock.mock_calls, expected_calls )

    def test_calls_read_socket_less_than_2097152( self ):
        self.rwo.readSock.side_effect = [ b'\xdf', b'\xff\xf4' ]
        self.rwo.getLen()
        expected_calls = [ call(1), call(2) ]
        self.assertEqual( self.rwo.readSock.mock_calls, expected_calls )

    def test_calls_read_socket_less_than_268435456( self ):
        self.rwo.readSock.side_effect = [ b'\xef', b'\xff\xff\xf0' ]
        self.rwo.getLen()
        expected_calls = [ call(1), call(3) ]
        self.assertEqual( self.rwo.readSock.mock_calls, expected_calls )



@patch('librouteros.connections.enclen')
class EncodeWord(unittest.TestCase):

    def test_calls_enclen( self, enclen_mock ):
        word = 'word'
        conn.encword( word )
        enclen_mock.called_once_with( 4 )

    def test_returns_bytes_encoded(self, enclen_mock):
        enclen_mock.return_value = b'len'
        retval = conn.encword( 'word' )
        self.assertEqual( retval, b'lenword' )



@patch('librouteros.connections.encword')
class EncodeSentence(unittest.TestCase):

    def test_calls_encword( self, enc_word_mock ):
        sentence = ('first', 'second')
        enc_word_mock.side_effect = [ b'first', b'second' ]
        conn.encsnt( sentence )
        expected_calls = [ call(elem) for elem in sentence ]
        self.assertEqual( enc_word_mock.mock_calls, expected_calls )

    def test_returns_bytes_encoded_sentence(self, enc_word_mock):
        enc_word_mock.side_effect = [ b'first', b'second' ]
        retval = conn.encsnt(( 'first', 'second' ))
        self.assertEqual( retval, b'firstsecond\x00' )

    def test_appends_end_of_sentence_mark_ath_the_end(self, enc_word_mock):
        enc_word_mock.side_effect = [ b'' ]
        retval = conn.encsnt( ('',) )
        self.assertEqual( b'\x00', retval )




class DecodeSentences(unittest.TestCase):


    def test_return_decoded(self):
        retval = conn.decsnt( (b'first', b'second') )
        self.assertEqual( retval, ('first', 'second') )




class WriteSock(unittest.TestCase):


    def setUp(self):
        sock = MagicMock( spec = socket )
        self.rwo = conn.ReaderWriter( sock, None )


    def test_loops_as_long_as_string_is_not_sent(self):
        self.rwo.sock.send.side_effect = [ 2,2 ]
        self.rwo.writeSock( 'word' )
        expected_calls = [ call( 'word' ), call('rd') ]
        self.assertEqual( self.rwo.sock.send.mock_calls, expected_calls )


    def test_sending_raises_when_no_bytes_sent(self):
        self.rwo.sock.send.side_effect = [ 0 ]
        self.assertRaises( ConnError, self.rwo.writeSock, 'word' )


    def test_sending_raises_socket_timeout(self):
        self.rwo.sock.send.side_effect = SOCKET_TIMEOUT
        self.assertRaises( ConnError, self.rwo.writeSock, 'word' )


    def test_sending_raises_socket_error(self):
        self.rwo.sock.send.side_effect = SOCKET_ERROR
        self.assertRaises( ConnError, self.rwo.writeSock, 'word' )


    def test_does_not_call_socket_send_when_called_with_empty_string(self):
        self.rwo.writeSock('')
        self.assertEqual( self.rwo.sock.send.call_count, 0 )



class ReadSock(unittest.TestCase):


    def setUp(self):
        sock = MagicMock( spec = socket )
        self.rwo = conn.ReaderWriter( sock, None )

    def test_returns_empty_byte_when_called_with_0(self):
        retval = self.rwo.readSock(0)
        self.assertEqual( retval, b'' )

    def test_loops_as_long_as_are_bytes_to_receive(self):
        self.rwo.sock.recv.side_effect = [ b'wo', b'rd' ]
        self.rwo.readSock( 4 )
        expected_calls = [ call(4), call(2) ]
        self.assertEqual( self.rwo.sock.recv.mock_calls, expected_calls )

    def test_reading_raises_when_no_bytes_received(self):
        self.rwo.sock.recv.side_effect = [ b'' ]
        self.assertRaises( ConnError, self.rwo.readSock, 4 )

    def test_reading_raises_socket_timeout(self):
        self.rwo.sock.recv.side_effect = SOCKET_TIMEOUT
        self.assertRaises( ConnError, self.rwo.readSock, 4 )

    def test_reading_raises_socket_error(self):
        self.rwo.sock.recv.side_effect = SOCKET_ERROR
        self.assertRaises( ConnError, self.rwo.readSock, 4 )

    def test_returns_bytes_object(self):
        self.rwo.sock.recv.side_effect = [ b'wo', b'rd' ]
        retval = self.rwo.readSock( 4 )
        self.assertEqual( retval, b'word' )

    def test_does_not_call_recv_when_called_with_0(self):
        self.rwo.readSock(0)
        self.assertEqual( self.rwo.sock.recv.call_count, 0 )



@patch('librouteros.connections.log_snt')
@patch('librouteros.connections.encsnt')
class WriteSentence(unittest.TestCase):


    def setUp(self):
        self.rwo = conn.ReaderWriter( None, None )
        self.rwo.writeSock = MagicMock()

    def test_calls_encode_sentence( self, encsnt_mock, log_mock ):
        sentence = ('first', 'second')
        self.rwo.writeSnt( sentence )
        encsnt_mock.assert_called_once_with( sentence )

    def test_calls_writeSock( self, encsnt_mock, log_mock ):
        encsnt_mock.return_value = 'encoded'
        self.rwo.writeSnt( 'sentence' )
        self.rwo.writeSock.assert_called_once_with( 'encoded' )

    def test_calls_log_sentence(self, encsnt_mock, log_mock):
        self.rwo.writeSnt('sentence')
        log_mock.assert_called_once_with( None, 'sentence', 'write' )



@patch('librouteros.connections.log_snt')
@patch('librouteros.connections.decsnt')
class ReadSentence(unittest.TestCase):


    def setUp(self):
        self.rwo = conn.ReaderWriter( None, None )
        self.rwo.readSock = MagicMock( side_effect = [ 'first','second' ] )
        self.rwo.getLen = MagicMock( side_effect = [5,6,0] )


    def test_calls_getLen_as_long_as_returns_0( self, decsnt_mock, log_mock ):
        self.rwo.readSnt()
        self.assertEqual( self.rwo.getLen.call_count, 3 )

    def test_calls_readSock_for_every_returned_getLen(self, decsnt_mock, log_mock):
        self.rwo.readSnt()
        self.assertEqual( self.rwo.readSock.mock_calls, [ call(5), call(6) ] )

    def test_calls_decode_sentence( self, decsnt_mock, log_mock ):
        self.rwo.readSnt()
        decsnt_mock.assert_called_once_with( [ 'first', 'second' ] )

    def test_calls_log_sentence(self, decsnt_mock, log_mock):
        decsnt_mock.return_value = 'string'
        self.rwo.readSnt()
        log_mock.assert_called_once_with( None, 'string', 'read' )


class ClosingProcedures(unittest.TestCase):


    def setUp(self):
        sock = MagicMock( spec = socket )
        self.rwo = conn.ReaderWriter( sock, None )


    def test_does_not_call_close_if_socket_already_is_closed(self):
        self.rwo.sock._closed = True
        self.assertEqual( self.rwo.sock.close.call_count, 0 )

    def test_does_not_call_shutdown_if_socket_already_is_closed(self):
        self.rwo.sock._closed = True
        self.assertEqual( self.rwo.sock.shutdown.call_count, 0 )

    def test_call_close_if_socket_is_not_closed(self):
        self.rwo.sock._closed = False
        self.rwo.close()
        self.rwo.sock.close.assert_called_once_with()

    def test_call_shutdown_if_socket_is_not_closed(self):
        self.rwo.sock._closed = False
        self.rwo.close()
        self.rwo.sock.shutdown.assert_called_once_with( SHUT_RDWR )

    def test_calls_socket_close_even_if_shutdown_raises_socket_error(self):
        self.rwo.sock._closed = False
        self.rwo.sock.shutdown.side_effect = SOCKET_ERROR()
        self.rwo.close()
        self.rwo.sock.close.assert_called_once_with()
