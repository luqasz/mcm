# -*- coding: UTF-8 -*-

import pytest
from socket import SHUT_RDWR, error as SOCKET_ERROR, timeout as SOCKET_TIMEOUT, socket
from mock import MagicMock, patch

from mcm.librouteros import connections
from mcm.librouteros.exceptions import ConnectionError, FatalError


integers = (0, 127, 130, 2097140, 268435440)
encoded = (b'\x00', b'\x7f', b'\x80\x82', b'\xdf\xff\xf4', b'\xef\xff\xff\xf0')


class Test_Decoder:

    @pytest.mark.parametrize("length,expected", (
        (b'x', 0),  # 120
        (b'\xbf', 1),  # 191
        (b'\xdf', 2),  # 223
        (b'\xef', 3),  # 239
        ))
    def test_determineLength(self, length, expected):
        assert connections.Decoder.determineLength(length) == expected

    def test_raises_if_integer_is_too_big(self):
        '''Raises ConnectionError if length >= 240'''
        bad_length = b'\xf0'
        with pytest.raises(ConnectionError) as error:
            connections.Decoder.determineLength(bad_length)
        assert str(bad_length) in str(error.value)

    @pytest.mark.parametrize("encoded,integer", zip(encoded, integers))
    def test_decodeLength(self, encoded, integer):
        assert connections.Decoder.decodeLength(encoded) == integer

    def test_raises_if_bytes_is_too_big(self):
        '''Raises ConnectionError if length > 4 bytes'''
        bad_length = b'\xff\xff\xff\xff\xff'
        with pytest.raises(ConnectionError) as error:
            connections.Decoder.decodeLength(bad_length)
        assert str(bad_length) in str(error.value)


class Test_Encoder:

    @pytest.mark.parametrize("integer,encoded", zip(integers, encoded))
    def test_encodeLength(self, integer, encoded):
        assert connections.Encoder.encodeLength(integer) == encoded

    def test_encodeLength_raises_if_lenghth_is_too_big(self):
        '''Raises ConnectionError if length >= 268435456'''
        bad_length = 268435456
        with pytest.raises(ConnectionError) as error:
            connections.Encoder.encodeLength(bad_length)
        assert str(bad_length) in str(error.value)

    def test_encodeWord_returns_encoded_word(self):
        assert connections.Encoder.encodeWord('word')[-4:] == b'word'

    @patch.object(connections.Encoder, 'encodeLength')
    def test_encodeWord_calls_encodeLength(self, encodeLength_mock):
        connections.Encoder.encodeWord('word')
        assert encodeLength_mock.call_count == 1

    @patch.object(connections.Encoder, 'encodeLength', return_value=b'len_')
    def test_encodeWord_returns_word_with_prefixed_length(self, encodeLength_mock):
        assert connections.Encoder.encodeWord('word') == b'len_word'

    def test_non_ASCII_word_encoding(self):
        with pytest.raises(UnicodeEncodeError):
            connections.Encoder.encodeWord('łą')

    @patch.object(connections.Encoder, 'encodeWord', return_value=b'')
    def test_encodeSentence_calls_encodeWord(self, encodeWord_mock):
        connections.Encoder.encodeSentence(('first', 'second'))
        assert encodeWord_mock.call_count == 2

    @patch.object(connections.Encoder, 'encodeWord', return_value=b'')
    def test_encodeSentence_appends_EOS_ath_the_end(self, encodeWord_mock):
        assert connections.Encoder.encodeSentence(('first', 'second'))[-1:] == b'\x00'


class Test_ApiProtocol:

    def setup(self):
        self.protocol = connections.ApiProtocol(transport=MagicMock(spec=connections.SocketTransport))

    @patch.object(connections.Encoder, 'encodeSentence')
    def test_writeSentence_calls_encodeSentence(self, encodeSentence_mock):
        self.protocol.writeSentence(cmd=b'/ip/address/print', words=(b'=key=value',))
        encodeSentence_mock.assert_called_once_with((b'/ip/address/print', b'=key=value'))

    @patch.object(connections.Encoder, 'encodeSentence')
    def test_writeSentence_calls_transport_write(self, encodeSentence_mock):
        '''Assert that write is called with encoded sentence.'''
        self.protocol.writeSentence(cmd=b'/ip/address/print', words=(b'=key=value',))
        self.protocol.transport.write.assert_called_once_with(encodeSentence_mock.return_value)

    @patch.object(connections.Decoder, 'decodeLength')
    @patch.object(connections.Decoder, 'determineLength')
    def test_readLength_calls_decodeLength(self, determineLength_mock, decodeLength_mock):
        '''Case when there are no additional bytes to read.'''
        self.protocol.transport.read.side_effect = [b'\x00', b'']
        self.protocol.readLength()
        decodeLength_mock.assert_called_once_with(b'\x00')

    @patch.object(connections.Decoder, 'decodeLength')
    @patch.object(connections.Decoder, 'determineLength')
    def test_readLength_calls_determineLength(self, determineLength_mock, decodeLength_mock):
        '''Check if determineLength is called only once with first read byte.'''
        self.protocol.transport.read.side_effect = [b'\x00', b'\x01']
        self.protocol.readLength()
        determineLength_mock.assert_called_once_with(b'\x00')

    @patch.object(connections.Decoder, 'decodeLength')
    @patch.object(connections.Decoder, 'determineLength')
    def test_readLength_calls_transport_read_with_determineLength_return_value(self, determineLength_mock, decodeLength_mock):
        self.protocol.readLength()
        self.protocol.transport.read.assert_any_call(determineLength_mock.return_value)

    def test_readWord_calls_transport_read(self):
        self.protocol.readWord(2)
        self.protocol.transport.read.assert_called_once_with(2)

    def test_readWord_raises_UnicodeDecodeError(self):
        self.protocol.transport.read.side_effect = [b'\xc5\x82\xc4\x85']
        with pytest.raises(UnicodeDecodeError):
            self.protocol.readWord(2)

    def test_readWord_decodes_bytes(self):
        self.protocol.transport.read.side_effect = [b'word']
        assert self.protocol.readWord(2) == 'word'

    @patch.object(connections.ApiProtocol, 'readWord')
    @patch.object(connections.ApiProtocol, 'readLength')
    def test_readSentence_calls_readWord(self, readLength_mock, readWord_mock):
        '''Assert that read is called as long as readLength does not return 0.'''
        readLength_mock.side_effect = [1, 0]
        self.protocol.readSentence()
        readWord_mock.assert_called_once_with(1)

    @patch.object(connections.ApiProtocol, 'readWord')
    @patch.object(connections.ApiProtocol, 'readLength')
    def test_readSentence_raises_FatalError(self, readLength_mock, readWord_mock):
        '''Assert that FatalError is raised with its reason.'''
        readWord_mock.side_effect = ['!fatal', 'reason']
        readLength_mock.side_effect = [1, 1, 0]
        with pytest.raises(FatalError) as error:
            self.protocol.readSentence()
        assert str(error.value) == 'reason'


class Test_SocketTransport:

    def setup(self):
        self.transport = connections.SocketTransport(sock=MagicMock(spec=socket))

    def test_calls_shutdown(self):
        self.transport.close()
        self.transport.sock.shutdown.assert_called_once_with(SHUT_RDWR)

    def test_calls_socket_close_even_if_shutdown_raises_socket_error(self):
        self.transport.sock.shutdown.side_effect = SOCKET_ERROR
        self.transport.close()
        self.transport.sock.close.assert_called_once_with()

    def test_calls_sendall(self):
        self.transport.write(b'some message')
        self.transport.sock.sendall.assert_called_once_with(b'some message')

    @pytest.mark.parametrize("exception", (SOCKET_ERROR, SOCKET_TIMEOUT))
    def test_write_raises_socket_errors(self, exception):
        self.transport.sock.sendall.side_effect = exception
        with pytest.raises(ConnectionError):
            self.transport.write(b'some data')

    def test_does_not_call_sendall(self):
        self.transport.write(b'')
        assert self.transport.sock.send.call_count == 0

    def test_returns_empty_byte_string(self):
        assert self.transport.read(0) == b''

    def test_loops_reading(self):
        self.transport.sock.recv.side_effect = [b'wo', b'rd']
        assert self.transport.read(4) == b'word'

    def test_raises_when_no_bytes_received(self):
        self.transport.sock.recv.side_effect = [b'']
        with pytest.raises(ConnectionError):
            self.transport.read(4)

    @pytest.mark.parametrize("exception", (SOCKET_ERROR, SOCKET_TIMEOUT))
    def test_read_raises_socket_errors(self, exception):
        self.transport.sock.recv.side_effect = exception
        with pytest.raises(ConnectionError):
            self.transport.read(2)

    def test_does_not_call_recv(self):
        self.transport.read(0)
        assert self.transport.sock.recv.call_count == 0
