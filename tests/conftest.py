import pytest
from logging import getLogger, NullHandler

NULL_LOGGER = getLogger('api_null_logger')
NULL_LOGGER.addHandler(NullHandler())


@pytest.fixture(scope='function')
def lib_default_kwargs():
    return {
            'timeout': 10,
            'port': 8728,
            'saddr': '',
            'logger': NULL_LOGGER,
            }
