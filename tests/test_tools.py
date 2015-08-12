# -*- coding: UTF-8 -*-

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch
from unittest import TestCase, skipIf
from sys import version_info

try:
    from time import monotonic
except ImportError:
    from time import time
import operator


from tools import StopWatch, timer, vcmp, ChainMap



class TimerFunctionImport(TestCase):

    @skipIf( version_info.major >= 3 and version_info.minor < 3, 'Requires python >= 3.3' )
    def test_module_uses_monotonic_as_timer(self):
        '''Assert that time.monotonic is used.'''
        self.assertTrue( timer == monotonic )

    @skipIf( version_info.major >= 3 and version_info.minor > 2, 'Using python >= 3.3' )
    def test_module_uses_time_as_timer(self):
        '''Assert that time.time is used when time.monotonic is not available.'''
        self.assertTrue( timer == time )




@patch('tools.timer', side_effect=[14705.275287508, 14711.190629636])
class StopWatchTests(TestCase):

    def setUp(self):
        self.TestCls = StopWatch()

    def test_sets_start_value_on_entering(self, timermock):
        with self.TestCls as st:
            self.assertEqual(st.start, 14705.275287508)

    def test_sets_stop_value_on_exiting(self, timermock):
        with self.TestCls as st:
            pass
        self.assertEqual(st.stop, 14711.190629636)

    def test_calculates_runtime_value_rounded_to_2_digits(self, timermock):
        with self.TestCls as st:
            pass
        self.assertEqual( st.runtime, 5.92 )



class VersionCompareTests(TestCase):

    def test_greater_then_returns_True(self):
        """Return True when first is greater than second."""
        result = vcmp( '4.11', '3.12', operator.gt )
        self.assertTrue( result )

    def test_greater_then_returns_False(self):
        """Return False when first is not greater than second."""
        result = vcmp( '4.11', '5.12', operator.gt )
        self.assertFalse( result )


    def test_greater_or_equel_returns_True_when_same_versions(self):
        result = vcmp( '4.11', '4.11', operator.ge )
        self.assertTrue( result )

    def test_greater_or_equel_returns_True_when_different_versions(self):
        result = vcmp( '4.14', '4.11', operator.ge )
        self.assertTrue( result )

    def test_greater_or_equal_returns_False(self):
        result = vcmp( '4.11', '5.12', operator.ge )
        self.assertFalse( result )


    def test_less_then_comparison_returns_True(self):
        result = vcmp( '4.11', '5.12', operator.lt )
        self.assertTrue( result )

    def test_less_then_comparison_returns_False(self):
        result = vcmp( '6.11', '5.12', operator.lt )
        self.assertFalse( result )


    def test_less_or_equel_comparison_returns_True_when_same_versions(self):
        result = vcmp( '4.11', '4.11', operator.le )
        self.assertTrue( result )

    def test_less_or_equel_comparison_returns_True_when_different_versions(self):
        result = vcmp( '4.1', '4.11', operator.le )
        self.assertTrue( result )

    def test_less_or_equal_comparison_returns_False(self):
        result = vcmp( '6.11', '5.12', operator.le )
        self.assertFalse( result )


    def test_equal_comparison_returns_True(self):
        result = vcmp( '4.11', '4.11', operator.eq )
        self.assertTrue( result )

    def test_equal_comparison_returns_False(self):
        result = vcmp( '4.10', '4.1', operator.eq )
        self.assertFalse( result )


    def test_not_equal_comparison_returns_True(self):
        result = vcmp( '4.10', '4.1', operator.ne )
        self.assertTrue( result )

    def test_not_equal_comparison_returns_False(self):
        result = vcmp( '4.11', '4.11', operator.ne )
        self.assertFalse( result )


class ChainMapTests(TestCase):

    def setUp(self):
        self.default_dict = dict(port=123, timeout=10)
        self.override_dict = dict(username='admin', host='1.1.1.1', port=222)
        self.chained = ChainMap(self.override_dict, self.default_dict)

    def test_raises_KeyError_if_key_is_not_found(self):
        with self.assertRaises(KeyError):
            self.chained['not_found']

    def test_timeout_is_equal_to_key_value_in_default_dict(self):
        self.assertEqual(self.chained['timeout'], self.default_dict['timeout'])

    def test_port_is_equal_to_key_value_from_overrided_dict(self):
        self.assertEqual(self.chained['port'], self.override_dict['port'])

