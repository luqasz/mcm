# -*- coding: UTF-8 -*-

# by default try to use monotonic timer witch is not subjected to local machine time changes
try:
    from time import monotonic as timer
except ImportError:
    from time import time as timer

from distutils.version import LooseVersion
from collections import UserDict


class StopWatch:

    def __enter__(self):
        self.start = timer()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop = timer()
        self.runtime = round((self.stop - self.start), 2)
        return False


def vcmp(v1, v2, op):
    '''
    Compare v1 and v2 using op.

    op:
        operator.op object
    '''

    v1 = str(v1)
    v2 = str(v2)

    return op(LooseVersion(v1), LooseVersion(v2))


class ChainMap(UserDict):
    '''
    Fallback collections.ChainMap if using python3 < 3.4
    '''

    def __init__(self, *maps):
        self._maps = maps

    def __getitem__(self, key):
        for mapping in self._maps:
            try:
                return mapping[key]
            except KeyError:
                pass
        raise KeyError(key)
