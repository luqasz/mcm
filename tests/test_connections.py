# -*- coding: UTF-8 -*-

import unittest
import pytest
from socket import SHUT_RDWR, error as SOCKET_ERROR, timeout as SOCKET_TIMEOUT, socket
from mock import MagicMock, call, patch

from mcm.librouteros import connections
from mcm.librouteros.exceptions import ConnError


integers = (0, 127 ,130 ,2097140 ,268435440)
encoded = (b'\x00', b'\x7f', b'\x80\x82', b'\xdf\xff\xf4', b'\xef\xff\xff\xf0')


@pytest.mark.parametrize("integer,encoded", zip(integers, encoded))
def test_encoding(integer, encoded):
    assert connections.enclen(integer) == encoded


@pytest.mark.parametrize("encoded,integer", zip(encoded, integers))
def test_decoding(encoded, integer):
    assert connections.declen(encoded) == integer


def test_raises_ConnError_if_lenghth_is_too_big():
    '''Raises ConnError if length >= 268435456'''
    with pytest.raises(ConnError):
        connections.enclen(268435456)


def test_raises_ConnError_if_bytes_is_too_big():
    '''Raises ConnError if length > 4 bytes'''
    with pytest.raises(ConnError):
        connections.declen(b'\xff\xff\xff\xff\xff')


@patch('mcm.librouteros.connections.enclen', return_value=b'len')
def test_word_encode_returns_encoded_word_with_prefixed_length(enclen_mock):
    assert connections.encword('word') == b'lenword'

@patch('mcm.librouteros.connections.enclen')
def test_non_ASCII_word_encoding(enclen_mock):
    with pytest.raises(ConnError) as error:
        connections.encword('łą')
    assert 'łą' in str(error.value)


@patch('mcm.librouteros.connections.encword', side_effect = [ b'first', b'second' ])
class EncodeSentence(unittest.TestCase):

    def test_calls_encword( self, enc_word_mock ):
        sentence = ('first', 'second')
        connections.encsnt( sentence )
        assert enc_word_mock.mock_calls == [ call(elem) for elem in sentence ]

    def test_returns_bytes_encoded_sentence_with_appended_EOS(self, enc_word_mock):
        assert connections.encsnt(( 'first', 'second' )) == b'firstsecond\x00'


def test_sentence_decoding():
    assert connections.decsnt( (b'first', b'second') ) == ('first', 'second')

def test_non_ASCII_sentence_decoding():
    non_ascii = b'\xc5\x82\xc4\x85'
    with pytest.raises(ConnError) as error:
        connections.decsnt((non_ascii,))
    assert str(non_ascii) in str(error.value)



@patch('mcm.librouteros.connections.declen')
class GetLengths(unittest.TestCase):


    def setUp(self):
        self.rwo = connections.ReaderWriter( None, None )
        self.rwo.readSock = MagicMock()

    def test_calls_declen(self, dec_len_mock):
        self.rwo.readSock.side_effect = [b'\x7f', b'']
        self.rwo.getLen()
        dec_len_mock.assert_called_once_with( b'\x7f' )

    def test_raises_if_first_byte_if_greater_than_239( self , dec_len_mock):
        self.rwo.readSock.return_value = b'\xf0'
        self.assertRaises( ConnError, self.rwo.getLen )

    def test_calls_read_socket_less_than_128( self , dec_len_mock):
        self.rwo.readSock.side_effect = [b'\x7f', b'']
        self.rwo.getLen()
        expected_calls = [ call(1), call(0) ]
        self.assertEqual( self.rwo.readSock.mock_calls, expected_calls )

    def test_calls_read_socket_less_than_16384( self , dec_len_mock):
        self.rwo.readSock.side_effect = [ b'\x80', b'\x82' ]
        self.rwo.getLen()
        expected_calls = [ call(1), call(1) ]
        self.assertEqual( self.rwo.readSock.mock_calls, expected_calls , dec_len_mock)

    def test_calls_read_socket_less_than_2097152( self , dec_len_mock):
        self.rwo.readSock.side_effect = [ b'\xdf', b'\xff\xf4' ]
        self.rwo.getLen()
        expected_calls = [ call(1), call(2) ]
        self.assertEqual( self.rwo.readSock.mock_calls, expected_calls )

    def test_calls_read_socket_less_than_268435456( self , dec_len_mock):
        self.rwo.readSock.side_effect = [ b'\xef', b'\xff\xff\xf0' ]
        self.rwo.getLen()
        expected_calls = [ call(1), call(3) ]
        self.assertEqual( self.rwo.readSock.mock_calls, expected_calls )






class Test_socket_writing:


    def setup(self):
        self.connection = connections.ReaderWriter( sock=MagicMock(), log=None )

    def test_calls_sendall(self):
        self.connection.writeSock(b'some message')
        self.connection.sock.sendall.assert_called_once_with(b'some message')

    @pytest.mark.parametrize("exception", (SOCKET_ERROR, SOCKET_TIMEOUT))
    def test_raises_socket_errors(self, exception):
        self.connection.sock.sendall.side_effect = exception
        with pytest.raises(ConnError):
            self.connection.writeSock(b'some data')

    def test_does_not_call_sendall(self):
        self.connection.writeSock(b'')
        assert self.connection.sock.send.call_count == 0



class Test_socket_reading:


    def setup(self):
        self.connection = connections.ReaderWriter( sock=MagicMock(), log=None )

    def test_returns_empty_byte_string(self):
        assert self.connection.readSock(0) == b''

    def test_loops_reading(self):
        self.connection.sock.recv.side_effect = [ b'wo', b'rd' ]
        assert self.connection.readSock( 4 ) == b'word'

    def test_raises_when_no_bytes_received(self):
        self.connection.sock.recv.side_effect = [ b'' ]
        with pytest.raises(ConnError):
            self.connection.readSock(4)

    @pytest.mark.parametrize("exception", (SOCKET_ERROR, SOCKET_TIMEOUT))
    def test_raises_socket_errors(self, exception):
        self.connection.sock.recv.side_effect = exception
        with pytest.raises(ConnError):
            self.connection.readSock(b'some data')

    def test_does_not_call_recv(self):
        self.connection.readSock(0)
        assert self.connection.sock.recv.call_count == 0



@patch('mcm.librouteros.connections.log_snt')
@patch('mcm.librouteros.connections.encsnt')
class WriteSentence(unittest.TestCase):


    def setUp(self):
        self.rwo = connections.ReaderWriter( None, None )
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



@patch('mcm.librouteros.connections.log_snt')
@patch('mcm.librouteros.connections.decsnt')
class ReadSentence(unittest.TestCase):


    def setUp(self):
        self.rwo = connections.ReaderWriter( None, None )
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
        self.rwo = connections.ReaderWriter( sock, None )


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
