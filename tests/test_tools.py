# -*- coding: UTF-8 -*-

from mock import patch
from sys import version_info
import operator
import pytest

try:
    from time import monotonic
except ImportError:
    from time import time

from mcm.tools import StopWatch, timer, vcmp, ChainMap


@pytest.mark.skipif( version_info < (3,3), reason='Requires python >= 3.3' )
def test_module_uses_monotonic_as_timer():
    '''Assert that time.monotonic is used.'''
    assert timer == monotonic

@pytest.mark.skipif( version_info > (3,2), reason='Using python >= 3.3' )
def test_module_uses_time_as_timer():
    '''Assert that time.time is used when time.monotonic is not available.'''
    assert timer == time


@pytest.mark.parametrize("v1,v2,oper,result", (
        ('4.11','3.12',operator.gt,True),
        ('4.11','5.12',operator.gt,False),
        ('4.11','4.11',operator.ge,True),
        ('4.14','4.11',operator.ge,True),
        ('4.11','5.12',operator.ge,False),
        ('4.11','5.12',operator.lt,True),
        ('6.11','5.12',operator.lt,False),
        ('4.11','4.11',operator.le,True),
        ('4.1','4.11',operator.le,True),
        ('6.11','5.12',operator.le,False),
        ('4.11','4.11',operator.eq,True),
        ('4.10','4.1',operator.eq,False),
        ('4.10','4.1',operator.ne,True),
        ('4.11','4.11',operator.ne,False),
        ))
def test_version_comparison(v1,v2,oper,result):
    assert vcmp(v1=v1,v2=v2,op=oper) == result


@patch('mcm.tools.timer', side_effect=[14705.275287508, 14711.190629636])
class Test_StopWatch:

    def test_sets_start_value_on_entering(self, timermock):
        with StopWatch() as st:
            assert st.start == 14705.275287508

    def test_sets_stop_value_on_exiting(self, timermock):
        with StopWatch() as st:
            pass
        assert st.stop == 14711.190629636

    def test_calculates_runtime_value_rounded_to_2_digits(self, timermock):
        with StopWatch() as st:
            pass
        assert st.runtime == 5.92


class Test_ChainMap:

    def setup(self):
        self.default_dict = dict(port=123, timeout=10)
        self.override_dict = dict(port=222)
        self.chained = ChainMap(self.override_dict, self.default_dict)

    def test_raises_KeyError_if_key_is_not_found(self):
        with pytest.raises(KeyError):
            self.chained['not_found']

    def test_timeout_is_equal_to_key_value_in_default_dict(self):
        assert self.chained['timeout'] == self.default_dict['timeout']

    def test_port_is_equal_to_key_value_from_overrided_dict(self):
        assert self.chained['port'] == self.override_dict['port']

