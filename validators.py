# -*- coding: UTF-8 -*-

from exceptions import ValidateError


def validate_list(lst, allowed):

    forbidden = set(lst) - set(allowed)
    if forbidden:
        raise ValidateError()

def validate_value(val, allowed):

    if val not in allowed:
        raise ValidateError()

def validate_type(val, allowed):

    if type(val) != allowed:
        raise ValidateError()
