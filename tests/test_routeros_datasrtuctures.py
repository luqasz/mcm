# -*- coding: UTF-8 -*-

import pytest

from mcm.librouteros.datastructures import parsresp, parsnt, mksnt, mkattrwrd, convattrwrd, castValToPy, castValToApi, raiseIfFatal, trapCheck
from mcm.librouteros.exceptions import CmdError, ConnError



def test_trap_string_in_sentences_raises_exception():
    with pytest.raises(CmdError):
        trapCheck(('!trap','=key=value'))


def test_raises_when_fatal():
    with pytest.raises(ConnError):
        raiseIfFatal(('!fatal','connection terminated by remote hoost'))


def test_does_not_raise_exception_if_no_fatal_string():
    raiseIfFatal( 'some string without error' )


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
def test_casting_from_api_to_python(api_type, python_type):
    assert castValToPy( api_type ) == python_type


@pytest.mark.parametrize("python_type,api_type", (
        (True, 'yes'),
        (False, 'no'),
        (None, ''),
        ('string', 'string'),
        ('22.2', '22.2'),
        (22.2, '22.2'),
        (22, '22'),
        ))
def test_casting_from_python_to_api(python_type, api_type):
    assert castValToApi(python_type) == api_type

api_words = (
        '=key=value',
        '=.id=value',
        )
key_value_tuples = (
        ('key','value'),
        ('.id','value'),
        )

@pytest.mark.parametrize("word,expected", zip(api_words,key_value_tuples))
def test_converting_api_word_to_tuple(word, expected):
    assert convattrwrd(word) == expected


@pytest.mark.parametrize("word,pair", zip(api_words,key_value_tuples))
def test_converting_tuple_to_api_word(word,pair):
    assert mkattrwrd(pair) == word


@pytest.mark.parametrize("sentence,api_sentence", (
    ( {'interface':'ether1','address':'1.1.1.1/23'}, ('=interface=ether1','=address=1.1.1.1/23') ),
    ( {'interface':'ether1','address':'1.1.1.1/23','.tag':2}, ('=interface=ether1','=address=1.1.1.1/23', '.tag=2') ),
    ))
def test_api_sentence_creation(sentence,api_sentence):
    assert set(mksnt(sentence)) == set(api_sentence)


@pytest.mark.parametrize("response,expected", (
    ( ( ('=disabled=no','.tag=1'),('.tag=4','!done') ), ({'disabled':False},)  ),
    ))
def test_api_response_parsing(response,expected):
    assert parsresp(response) == (expected)


@pytest.mark.parametrize("api_sentence,expected", (
    ( ('.tag=1','!done'), dict() ),
    ( ('=disabled=false','=interface=ether1','.tag=2'), {'disabled':False,'interface':'ether1'} ),
    ( ('=disabled=false','=interface=ether1'), {'disabled':False,'interface':'ether1'} ),
    ))
def test_api_sentence_parsing(api_sentence,expected):
    assert parsnt(api_sentence) == expected
