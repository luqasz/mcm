# -*- coding: UTF-8 -*-

import pytest
from mock import patch, MagicMock

from mcm.librouteros.api import Api, Composer, Parser
from mcm.librouteros.exceptions import ConnectionError, FatalError, TrapError


attribute_words = (
        '=.id=value',
        '=name=ether1',
        '=comment=',
        )


api_words = (
        '.tag=1',
        '.tag=1=2',
        )


attribute_pairs = (
        ('.id', 'value'),
        ('name', 'ether1'),
        ('comment', None),
        )


api_pairs = (
        ('.tag', 1),
        ('.tag', '1=2'),
        )


class Test_Parser:

    @pytest.mark.parametrize("api_type,python_type", (
            ('yes', True),
            ('no', False),
            ('true', True),
            ('false', False),
            ('', None),
            ('string', 'string'),
            ('22.2', '22.2'),
            ('22', 22),
            ))
    def test_apiCast(self, api_type, python_type):
        assert Parser.apiCast(api_type) == python_type

    @pytest.mark.parametrize("word, expected", zip(attribute_words + api_words, attribute_pairs + api_pairs))
    def test_parseWord(self, word, expected):
        assert Parser.parseWord(word) == expected


class Test_Composer:

    @pytest.mark.parametrize("python_type,api_type", (
            (True, 'yes'),
            (False, 'no'),
            (None, ''),
            ('string', 'string'),
            ('22.2', '22.2'),
            (22.2, '22.2'),
            (22, '22'),
            (1, '1'),
            (0, '0')
            ))
    def test_pythonCast(self, python_type, api_type):
        assert Composer.pythonCast(python_type) == api_type

    @pytest.mark.parametrize("pair, expected", zip(attribute_pairs, attribute_words))
    def test_composeAttributeWords(self, pair, expected):
        assert Composer.composeAttributeWords((pair,)) == (expected,)


class Test_Api:

    def setup(self):
        self.api = Api(transport=MagicMock(), protocol=MagicMock())

    @pytest.mark.parametrize("path, expected", (
        ("/ip/address/", "/ip/address"),
        ("ip/address", "/ip/address"),
        ("/ip/address", "/ip/address"),
        ))
    def test_joinPath_single_param(self, path, expected):
        assert self.api.joinPath(path) == expected

    @pytest.mark.parametrize("path, expected", (
        (("/ip/address/", "print"), "/ip/address/print"),
        (("ip/address", "print"), "/ip/address/print"),
        (("/ip/address", "set"), "/ip/address/set"),
        ))
    def test_joinPath_multi_param(self, path, expected):
        assert self.api.joinPath(*path) == expected

    # test dla case kiedy fatal error i ktos da pozniej close()
    # test dla !done z danymi i bez
