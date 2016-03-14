# -*- coding: UTF-8 -*-

import pytest
from mock import MagicMock

from mcm.librouteros.api import Api, Composer, Parser


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

    @pytest.mark.parametrize("read_sentence, expected_sentence, expected_tag", (
            (attribute_words + ('.tag=1',), dict(attribute_pairs), 1),
            (attribute_words, dict(attribute_pairs), None),
            ))
    def test_ParseWords(self, read_sentence, expected_sentence, expected_tag):
        parsed_tag, parsed_sentence = Parser.parseWords(read_sentence)
        assert expected_tag == parsed_tag
        assert parsed_sentence == expected_sentence


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

    def test_composeAttributeWords(self):
        assert Composer.composeAttributeWords(attribute_pairs) == attribute_words


class Test_Api:

    def setup(self):
        self.api = Api(protocol=MagicMock())

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
        (("/", "/ip/address", "set"), "/ip/address/set"),
        ))
    def test_joinPath_multi_param(self, path, expected):
        assert self.api.joinPath(*path) == expected
