# -*- coding: UTF-8 -*-

import pytest

from mcm.validators import validate_list, validate_value, validate_type
from mcm.exceptions import ValidateError


def test_validate_list_raises_ValidateError_when_list_passed_contains_forbidden_elements():
    with pytest.raises(ValidateError):
        validate_list(lst=[1, 2, 3], allowed=[1, 2])


def test_validate_val_raises_ValidateError_when_value_passed_is_not_in_allowed():
    with pytest.raises(ValidateError):
        validate_value(val='abc', allowed=('single', 'generic'))


def test_validate_type_raises_ValidateErrot_if_provided_value_is_not_the_same_type():
    with pytest.raises(ValidateError):
        validate_type(val=1, allowed=str)
