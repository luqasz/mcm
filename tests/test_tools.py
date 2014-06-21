# -*- coding: UTF-8 -*-

try:
    from unittest.mock import MagicMock, patch, call, PropertyMock
except ImportError:
    from mock import MagicMock, patch, call, PropertyMock
from unittest import TestCase, skipIf
from sys import version_info

try:
    from time import monotonic as test_timer
except ImportError:
    from time import time as test_timer
import operator


from tools import StopWatch, timer, vcmp



class TimerFunctionImport(TestCase):

    @skipIf( version_info.major >= 3 and version_info.minor < 3, 'monotonic timer available only on python => 3.3' )
    def test_module_uses_monotonic_timer(self):
        self.assertTrue( timer == test_timer )

    @skipIf( version_info.major >= 3 and version_info.minor > 3, 'using python >= 3.3' )
    def test_module_fallbacks_to_time_function(self):
        self.assertTrue( timer == test_timer )




class StopWatchTests(TestCase):

    def test_runtime_attribute_is_None_after_instantiation(self):
        st = StopWatch()
        self.assertEqual(st.runtime, None)

    @patch.object(StopWatch, 'calc')
    @patch('tools.timer')
    def test_enter_calls_timer_function(self, timermock, calcmock):
        StopWatch().__enter__()
        timermock.assert_called_once_with()

    @patch.object(StopWatch, 'calc')
    @patch('tools.timer')
    def test_exit_calls_timer_function(self, timermock, calcmock):
        StopWatch().__exit__(None,None,None)
        timermock.assert_called_once_with()

    @patch.object(StopWatch, 'calc')
    @patch('tools.timer')
    def test_exit_calls_calc(self, timermock, calcmock):
        StopWatch().__exit__(None, None, None)
        calcmock.assert_called_once_with()

    def test_calc_calculates_value_rounded_to_2_digits(self):
        st = StopWatch()
        st.start = 14705.275287508
        st.stop = 14711.190629636
        st.calc()
        self.assertEqual( st.runtime, 5.92 )



class VersionCompareTests(TestCase):

    def test_greater_then_comparison_returns_True(self):
        result = vcmp( '4.11', '3.12', operator.gt )
        self.assertTrue( result )

    def test_greater_then_comparison_returns_False(self):
        result = vcmp( '4.11', '5.12', operator.gt )
        self.assertFalse( result )


    def test_greater_or_equel_comparison_returns_True_when_same_versions(self):
        result = vcmp( '4.11', '4.11', operator.ge )
        self.assertTrue( result )

    def test_greater_or_equel_comparison_returns_True_when_different_versions(self):
        result = vcmp( '4.14', '4.11', operator.ge )
        self.assertTrue( result )

    def test_greater_or_equal_comparison_returns_False(self):
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
