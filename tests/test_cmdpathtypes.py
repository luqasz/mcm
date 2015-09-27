# -*- coding: UTF-8 -*-

import re
import pytest

from mcm.cmdpathtypes import MENU_PATHS


valid_path_types = ('single', 'ordered', 'uniquekey')
valid_modord_values = {'SET', 'ADD', 'DEL'}


@pytest.mark.parametrize("attribute_name,attribute_type",(
        ('type',str),
        ('keys',tuple),
        ('modord',tuple),
        ))
@pytest.mark.parametrize("path,attributes",MENU_PATHS.items())
def test_attributes_types(path,attributes,attribute_type,attribute_name):
    assert type(attributes[attribute_name]) == attribute_type, '{!r} is not {}'.format(attribute_name,attribute_type)


@pytest.mark.parametrize("path,attributes",MENU_PATHS.items())
def test_type_has_valid_value(path,attributes):
    assert attributes['type'] in valid_path_types, 'Invalid type {!r}'.format(attributes['type'])


@pytest.mark.parametrize("path,attributes",MENU_PATHS.items())
def test_modord_is_not_empty(path,attributes):
    assert attributes['modord'] != tuple(), 'Found empty modord in {}'.format(path)


@pytest.mark.parametrize("path,attributes",MENU_PATHS.items())
def test_modord_has_valid_attributes(path,attributes):
    to_check = set(attributes['modord'])
    assert to_check.issubset(valid_modord_values), 'Invalid modord value/s found {}'.format(to_check - valid_modord_values)


def assertNoDuplicates(to_check):
    duplicates = set([elem for elem in to_check if to_check.count(elem) > 1])
    if duplicates:
        raise AssertionError('Duplicated entries found: {}'.format('\n'.join(duplicates)))


def test_duplicated_entries():
    '''Check if there are any duplicated command path definitions.'''
    with open('mcm/cmdpathtypes.py') as definitions_file:
        content = definitions_file.read()
        found = re.findall(r'(?:\/[a-z0-9-]+)+', content)
        assertNoDuplicates(found)
