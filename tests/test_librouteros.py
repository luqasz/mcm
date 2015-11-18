#-*- coding: UTF-8 -*-

from socket import error as SOCKET_ERROR, timeout as SOCKET_TIMEOUT
from mock import MagicMock, patch
import pytest

from mcm.librouteros.exceptions import ConnectionError, LoginError, TrapError, FatalError
from mcm.librouteros import connect, encode_password



def test_password_encoding():
    assert encode_password( '259e0bc05acd6f46926dc2f809ed1bba', 'test') == '00c7fd865183a43a772dde231f6d0bff13'




