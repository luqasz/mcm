# -*- coding: UTF-8 -*-

try:
    from unittest.mock import MagicMock, patch, call
except ImportError:
    from mock import MagicMock, patch, call
from unittest import TestCase

from mcm.validators import validate_list, validate_value, validate_type
from mcm.exceptions import ValidateError


class ValidateListTests(TestCase):

    def test_validate_list_raises_ValidateError_when_list_passed_contains_forbidden_elements(self):
        self.assertRaises( ValidateError, validate_list, lst=[1,2,3], allowed=[1,2] )



class ValidateValueInTests(TestCase):

    def test_validate_val_raises_ValidateError_when_value_passed_is_not_in_allowed(self):
        self.assertRaises( ValidateError, validate_value, val='abc', allowed=('single', 'generic') )



class ValidateTypeTests(TestCase):

    def test_validate_type_raises_ValidateErrot_if_provided_value_is_not_the_same_type(self):
        self.assertRaises( ValidateError, validate_type, val=1, allowed=str )
