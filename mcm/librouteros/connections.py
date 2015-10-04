# -*- coding: UTF-8 -*-

from socket import SHUT_RDWR, error as SOCKET_ERROR, timeout as SOCKET_TIMEOUT
from struct import pack, unpack

from mcm.librouteros.exceptions import ConnError



def enclen( length ):
    '''
    Encode given length in mikrotik format.

    length: Integer < 268435456.
    returns: Encoded length in bytes.
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
        raise ConnError( 'unable to encode length of {}'
                        .format( length ) )

    encoded_length = pack( '!I', ored_length )[offset:]
    return encoded_length


def declen( bytes ):
    '''
    Decode length based on given bytes.

    bytes_string: Bytes string to decode.
    returns: Length in integer.
    '''

    bytes_length = len( bytes )

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
        raise ConnError( 'unable to decode length of {}'.format(bytes) )

    combined_bytes = offset + bytes
    decoded = unpack( '!I', combined_bytes )[0]
    decoded ^= XOR

    return decoded


def decsnt( sentence ):

    try:
        return tuple( word.decode( 'ASCII', 'strict' ) for word in sentence )
    except UnicodeDecodeError as error:
        raise ConnError('Could not decode {!r}. Non ASCII characters'.format(error.object))


def encsnt( sentence ):
    '''
    Encode given sentence in API format.

    returns: Encoded sentence in bytes object.
    '''

    encoded = map( encword, sentence )
    encoded = b''.join( encoded )
    # append EOS byte
    encoded += b'\x00'

    return encoded


def encword( word ):
    '''
    Encode word in API format.

    returns: Encoded word in bytes object.
    '''

    encoded_len = enclen( len( word ) )
    try:
        encoded_word = word.encode( encoding = 'ASCII', errors = 'strict' )
    except UnicodeEncodeError as error:
        raise ConnError('Could not encode {!r}. Non ASCII characters'.format(error.object))
    return encoded_len + encoded_word



def log_snt( logger, sentence, direction ):

    dstrs = { 'write':'<---', 'read':'--->' }
    dstr = dstrs.get( direction )

    for word in sentence:
        logger.debug( '{0} {1!r}'.format( dstr, word ) )

    logger.debug( '{0} EOS'.format( dstr ) )






class ReaderWriter:


    def __init__( self, sock, log ):
        self.sock = sock
        self.log = log


    def writeSnt( self, snt ):
        '''
        Write sentence to connection.

        sentence: Iterable (tuple or list) with words.
        '''

        encoded = encsnt( snt )
        self.writeSock( encoded )
        log_snt( self.log, snt, 'write' )


    def readSnt( self ):
        '''
        Read sentence from connection.

        returns: Sentence as tuple with words in it.
        '''

        snt = []
        for length in iter( self.getLen, 0 ):
            word = self.readSock( length )
            snt.append( word )

        decoded = decsnt( snt )
        log_snt( self.log, decoded, 'read' )

        return decoded


    def readSock( self, length ):
        '''
        Read as many bytes from socket as specified in length.
        Loop as long as every byte is read unless exception is raised.
        '''

        data = bytearray()
        to_read = length

        try:
            while to_read:
                read = self.sock.recv(to_read)
                if not read:
                    raise ConnError( 'Connection unexpectedly closed. read {read}/{total} bytes.'
                                    .format(read = len(data), total = length))
                data += read
                to_read -= len(read)

        except SOCKET_TIMEOUT:
            raise ConnError( 'Socket timed out. read {read}/{total} bytes.'
                            .format(read = len(data), total = length))
        except SOCKET_ERROR as estr:
            raise ConnError( 'Failed to read from socket. {reason}'.format(reason = estr))

        return data


    def writeSock( self, string ):
        '''
        Write given string to socket. Loop as long as every byte in
        string is written unless exception is raised.
        '''

        try:
            self.sock.sendall(string)
        except SOCKET_TIMEOUT as error:
            raise ConnError('Socket timed out. ' + str(error))
        except SOCKET_ERROR as error:
            raise ConnError('Failed to write to socket. ' + str(error))


    def getLen( self ):
        '''
        Read encoded length and return it as integer.
        '''

        first_byte = self.readSock( 1 )
        first_byte_int = unpack( 'B', first_byte )[0]

        if first_byte_int < 128:
            bytes_to_read = 0
        elif first_byte_int < 192:
            bytes_to_read = 1
        elif first_byte_int < 224:
            bytes_to_read = 2
        elif first_byte_int < 240:
            bytes_to_read = 3
        else:
            raise ConnError( 'unknown controll byte received {0!r}'
                            .format( first_byte ) )

        additional_bytes = self.readSock( bytes_to_read )

        return declen( first_byte + additional_bytes )


    def close( self ):

        # do not do anything if socket is already closed
        if self.sock._closed:
            return
        # shutdown socket
        try:
            self.sock.shutdown( SHUT_RDWR )
        except SOCKET_ERROR:
            pass
        finally:
            self.sock.close()
