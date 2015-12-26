# -*- coding: UTF-8 -*-

from socket import SHUT_RDWR, error as SOCKET_ERROR, timeout as SOCKET_TIMEOUT
from struct import pack, unpack
from logging import getLogger, NullHandler

from mcm.librouteros.exceptions import ConnectionError, FatalError

LOGGER = getLogger('librouteros')
LOGGER.addHandler(NullHandler())


class Encoder:

    @staticmethod
    def encodeSentence(sentence: tuple) -> tuple:
        '''
        Encode given sentence in API format.

        :param sentence: Sentence to endoce.
        :returns: Encoded sentence.
        '''
        encoded = map(Encoder.encodeWord, sentence)
        encoded = b''.join(encoded)
        # append EOS (end of sentence) byte
        encoded += b'\x00'
        return encoded

    @staticmethod
    def encodeWord(word: str) -> bytes:
        '''
        Encode word in API format.

        :param word: Word to encode.
        :returns: Encoded word.
        '''
        encoded_word = word.encode(encoding='ASCII', errors='strict')
        return Encoder.encodeLength(len(word)) + encoded_word

    @staticmethod
    def encodeLength(length: int) -> bytes:
        '''
        Encode given length in mikrotik format.

        :param length: Integer < 268435456.
        :returns: Encoded length.
        '''
        if length < 128:
            ored_length = length
            offset = -1
        elif length < 16384:
            ored_length = length | 0x8000
            offset = -2
        elif length < 2097152:
            ored_length = length | 0xC00000
            offset = -3
        elif length < 268435456:
            ored_length = length | 0xE0000000
            offset = -4
        else:
            raise ConnectionError('Unable to encode length of {}'.format(length))

        return pack('!I', ored_length)[offset:]


class Decoder:

    @staticmethod
    def determineLength(length: bytes) -> int:
        '''
        Given first read byte, determine how many more bytes
        needs to be known in order to get fully encoded length.

        :param length: First read byte.
        :return: How many bytes to read.
        '''
        integer = ord(length)

        if integer < 128:
            return 0
        elif integer < 192:
            return 1
        elif integer < 224:
            return 2
        elif integer < 240:
            return 3
        else:
            raise ConnectionError('Unknown controll byte {}'.format(length))

    @staticmethod
    def decodeLength(length: bytes) -> int:
        '''
        Decode length based on given bytes.

        :param length: Bytes string to decode.
        :return: Decoded length.
        '''
        bytes_length = len(length)

        if bytes_length < 2:
            offset = b'\x00\x00\x00'
            XOR = 0
        elif bytes_length < 3:
            offset = b'\x00\x00'
            XOR = 0x8000
        elif bytes_length < 4:
            offset = b'\x00'
            XOR = 0xC00000
        elif bytes_length < 5:
            offset = b''
            XOR = 0xE0000000
        else:
            raise ConnectionError('Unable to decode length of {}'.format(length))

        decoded = unpack('!I', (offset + length))[0]
        decoded ^= XOR
        return decoded


class ApiProtocol(Encoder, Decoder):

    def __init__(self, transport):
        self.transport = transport

    def log(self, sentence, direction_string):
        for word in sentence:
            LOGGER.debug('{0} {1!r}'.format(direction_string, word))

        LOGGER.debug('{0} EOS'.format(direction_string))

    def writeSentence(self, cmd: str, words: tuple = tuple()) -> None:
        '''
        Write encoded sentence.

        :param cmd: Command word.
        :param words: Aditional words.
        '''
        sentence = (cmd,) + words
        encoded = self.encodeSentence(sentence)
        self.log(sentence, '<---')
        self.transport.write(encoded)

    def readWord(self, length: int) -> str:
        '''
        Read single word.

        :param length: Length of word.
        :return: Decoded word.
        '''
        return self.transport \
                   .read(length) \
                   .decode(encoding='ASCII', errors='strict')

    def readSentence(self) -> tuple:
        '''
        Read every word untill empty word (NULL byte) is received.

        :return: Reply word, tuple with read words.
        '''
        sentence = tuple(self.readWord(length) for length in iter(self.readLength, 0))
        self.log(sentence, '--->')
        reply_word, words = sentence[0], sentence[1:]
        if reply_word == '!fatal':
            raise FatalError(words[0])
        else:
            return reply_word, words

    def readLength(self) -> int:
        '''
        Read length from transport. This method may return 0 which indicates end of sentence.

        :return: Length of next word.
        '''
        length = self.transport.read(1)
        to_read = self.determineLength(length)
        length += self.transport.read(to_read)
        return self.decodeLength(length)


class SocketTransport:

    def __init__(self, sock):
        self.sock = sock

    def write(self, string: bytes):
        '''
        Write given bytes string to socket. Loop as long as every byte in
        string is written unless exception is raised.
        '''
        try:
            self.sock.sendall(string)
        except SOCKET_TIMEOUT as error:
            raise ConnectionError('Socket timed out. ' + str(error))
        except SOCKET_ERROR as error:
            raise ConnectionError('Failed to write to socket. ' + str(error))

    def read(self, length: int) -> bytearray:
        '''
        Read as many bytes from socket as specified in length.
        Loop as long as every byte is read unless exception is raised.
        '''
        data = bytearray()
        try:
            while length:
                read = self.sock.recv(length)
                if not read:
                    msg = 'Connection unexpectedly closed. Read {read}/{total} bytes.'.format
                    raise ConnectionError(msg(read=len(data), total=(len(data) + length)))
                data += read
                length -= len(read)

        except SOCKET_TIMEOUT:
            msg = 'Socket timed out. Read {read}/{total} bytes.'.format
            raise ConnectionError(msg(read=len(data), total=(len(data) + length)))
        except SOCKET_ERROR as error:
            raise ConnectionError('Failed to read from socket. {reason}'.format(reason=error))

        return data

    def close(self):
        try:
            # inform other end that we will not read and write any more
            self.sock.shutdown(SHUT_RDWR)
        except SOCKET_ERROR:
            pass
        finally:
            self.sock.close()
