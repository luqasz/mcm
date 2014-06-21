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


from ctxtools import StopWatch, timer



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
    @patch('ctxtools.timer')
    def test_enter_calls_timer_function(self, timermock, calcmock):
        StopWatch().__enter__()
        timermock.assert_called_once_with()

    @patch.object(StopWatch, 'calc')
    @patch('ctxtools.timer')
    def test_exit_calls_timer_function(self, timermock, calcmock):
        StopWatch().__exit__(None,None,None)
        timermock.assert_called_once_with()

    @patch.object(StopWatch, 'calc')
    @patch('ctxtools.timer')
    def test_exit_calls_calc(self, timermock, calcmock):
        StopWatch().__exit__(None, None, None)
        calcmock.assert_called_once_with()

    def test_calc_calculates_value_rounded_to_2_digits(self):
        st = StopWatch()
        st.start = 14705.275287508
        st.stop = 14711.190629636
        st.calc()
        self.assertEqual( st.runtime, 5.92 )

