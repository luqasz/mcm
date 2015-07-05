# -*- coding: UTF-8 -*-

'''
from librouteros import connect
api = connect( '1.1.1.1', 'admin', 'password' )
api.run('/ip/address/print')
'''


from logging import getLogger, NullHandler
from socket import create_connection, error as sk_error, timeout as sk_timeout
from binascii import unhexlify, hexlify
from hashlib import md5
from collections import ChainMap

from librouteros.exc import ConnError, CmdError, LoginError
from librouteros.connections import ReaderWriter
from librouteros.api import Api

NULL_LOGGER = getLogger( 'api_null_logger' )
NULL_LOGGER.addHandler( NullHandler() )

__version__ = '1.1.0'


def connect( host, user, pw, **kwargs ):
    '''
    Connect and login to routeros device.
    Upon success return a Connection class.

    host
        Hostname to connecto to. May be ipv4,ipv6,FQDN.
    user
        Username to login with.
    pw
        Password to login with. Defaults to be empty.
    timout
        Socket timeout. Defaults to 10.
    port
        Destination port to be used. Defaults to 8728.
    logger
        Logger instance to be used. Defaults to an empty logging instance.
    saddr
        Source address to bind to.
    '''

    defaults = { 'timeout' : 10,
                'port' : 8728,
                'saddr' : '',
                'logger' : NULL_LOGGER
                }

    arguments = ChainMap(kwargs, defaults)

    try:
        sock = create_connection( ( host, arguments['port'] ), arguments['timeout'], ( arguments['saddr'], 0 ) )
    except ( sk_error, sk_timeout ) as e:
        raise ConnError( e )

    rwo = ReaderWriter( sock, arguments['logger'] )
    api = Api( rwo )

    try:
        snt = api.run( '/login' )
        chal = snt[0]['ret']
        encoded = _encpw( chal, pw )
        api.run( '/login', {'name':user, 'response':encoded} )
    except ( ConnError, CmdError ) as estr:
        rwo.close()
        raise LoginError( estr )

    return api



def _encpw( chal, password ):

    chal = chal.encode( 'UTF-8', 'strict' )
    chal = unhexlify( chal )
    password = password.encode( 'UTF-8', 'strict' )
    md = md5()
    md.update( b'\x00' + password + chal )
    password = hexlify( md.digest() )
    password = '00' + password.decode( 'UTF-8', 'strict' )

    return password


