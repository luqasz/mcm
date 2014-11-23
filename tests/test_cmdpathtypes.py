# -*- coding: UTF-8 -*-

from unittest import TestCase

from cmdpathtypes import MENU_PATHS

class CmdPathTypes_Tests(TestCase):

    def setUp(self):
        self.paths = MENU_PATHS.items()
        self.valid_types = ('single', 'ordered', 'uniquekey')

    def test_paths_type_is_string(self):
        for path, attrs in self.paths:
            self.assertIs(type(attrs['type']), str, msg='found in {}'.format(path))

    def test_paths_keys_is_tuple(self):
        for path, attrs in self.paths:
            self.assertIs(type(attrs['keys']), tuple, msg='found in {}'.format(path))

    def test_paths_modord_is_tupe(self):
        for path, attrs in self.paths:
            self.assertIs(type(attrs['modord']), tuple, msg='found in {}'.format(path))

    def test_paths_type_have_valid_value(self):
        for path, attrs in self.paths:
            self.assertIn(attrs['type'], self.valid_types, msg='Invalid type {} in {}'.format(attrs['type'], path))

    def test_modord_is_not_empty(self):
        for path, attrs in self.paths:
            self.assertNotEqual(attrs['modord'], tuple(), msg='found in {}'.format(path))

class CmdPathTypes_modord_value_Tests(TestCase):

    def setUp(self):
        self.paths = MENU_PATHS.items()
        self.addTypeEqualityFunc(tuple, self.ModordCheck)
        self.valid_modord = ('set', 'add', 'del')

    def ModordCheck(self, tested, valid, msg=None):
        result = set(tested) - set(valid)
        if result:
            result = ','.join(result)
            raise self.failureException('invalid value/s {!r} {}'.format(result, msg))

    def test_modord_has_valid_attributes(self):
        for path, attributes in self.paths:
            self.assertEqual(attributes['modord'], self.valid_modord, msg='found in {}'.format(path))
