# -*- coding: UTF-8 -*-


from logging import getLogger, NullHandler
from socket import create_connection, error as SOCKET_ERROR, timeout as SOCKET_TIMEOUT
from binascii import unhexlify, hexlify
from hashlib import md5
try:
    from collections import ChainMap
except ImportError:
    from mcm.tools import ChainMap

from mcm.librouteros.exceptions import TrapError, FatalError, ConnectionError
from mcm.librouteros.connections import ApiProtocol, SocketTransport
from mcm.librouteros.api import Api

NULL_LOGGER = getLogger('api_null_logger')
NULL_LOGGER.addHandler(NullHandler())

defaults = {
            'timeout': 10,
            'port': 8728,
            'saddr': '',
            'logger': NULL_LOGGER,
            }


def connect(host: str, username: str, password: str, **kwargs):
    '''
    Connect and login to routeros device.
    Upon success return a Connection class.

    :param host: Hostname to connecto to. May be ipv4,ipv6,FQDN.
    :param username: Username to login with.
    :param password: Password to login with. Only ASCII characters allowed.
    :param timout: Socket timeout. Defaults to 10.
    :param port: Destination port to be used. Defaults to 8728.
    :param logger: Logger instance to be used. Defaults to an empty logging instance.
    :param saddr: Source address to bind to.
    '''
    arguments = ChainMap(kwargs, defaults)
    transport = create_transport(host, **arguments)
    protocol = ApiProtocol(transport=transport, logger=arguments['logger'])
    api = Api(protocol=protocol, transport=transport)

    try:
        sentence = api('/login')
        token = sentence[0]['ret']
        encoded = encode_password(token, password)
        api('/login', {'name': username, 'response': encoded})
    except (ConnectionError, TrapError, FatalError):
        raise
    finally:
        transport.close()

    return api


def create_transport(host, **kwargs):
    try:
        sock = create_connection((host, kwargs['port']), kwargs['timeout'], (kwargs['saddr'], 0))
    except (SOCKET_ERROR, SOCKET_TIMEOUT) as error:
        raise ConnectionError(error)
    return SocketTransport(sock=sock)


def encode_password(token, password):

    token = token.encode('ascii', 'strict')
    token = unhexlify(token)
    password = password.encode('ascii', 'strict')
    md = md5()
    md.update(b'\x00' + password + token)
    password = hexlify(md.digest())
    return '00' + password.decode('ascii', 'strict')
