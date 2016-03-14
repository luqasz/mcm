import pytest
from mcm.librouteros import Api


@pytest.fixture(scope='function')
def lib_default_kwargs():
    return {
            'timeout': 10,
            'port': 8728,
            'saddr': '',
            'subclass': Api,
            }


@pytest.fixture(scope='function')
def bad_length_bytes():
    '''len(length) must be < 5'''
    return b'\xff\xff\xff\xff\xff'


@pytest.fixture(scope='function')
def bad_length_int():
    '''Length must be < 268435456'''
    return 268435456


@pytest.fixture(scope='function', params=(i.to_bytes(1, 'big') for i in range(240, 256)))
def bad_first_length_bytes(request):
    '''First byte of length must be < 240.'''
    return request.param


@pytest.fixture(scope='function', params=(
        (0, b'\x00'),
        (127, b'\x7f'),
        (130, b'\x80\x82'),
        (2097140, b'\xdf\xff\xf4'),
        (268435440, b'\xef\xff\xff\xf0'),
        )
        )
def length_pairs(request):
    '''Length as integer, encoded value.'''
    return request.param
