# -*- coding: UTF-8 -*-

import unittest
try:
    from unittest.mock import MagicMock, patch, call
except ImportError:
    from mock import MagicMock, patch, call

from tests_utils.equality_checks import SentenceEquality

from mcm.librouteros.datastructures import parsresp, parsnt, mksnt, mkattrwrd, convattrwrd, castValToPy, castValToApi, raiseIfFatal, trapCheck
from mcm.librouteros.exc import CmdError, ConnError



class TrapChecking(unittest.TestCase):


    def test_trap_in_sentences_raises(self):
        snts = ( '!trap', '=key=value' )
        self.assertRaises( CmdError, trapCheck, snts )


class RaiseIfFatal(unittest.TestCase):


    def test_raises_when_fatal(self):
        sentence = ('!fatal', 'connection terminated by remote hoost')
        self.assertRaises( ConnError,  raiseIfFatal, sentence )


    def test_does_not_raises_if_no_error(self):
        raiseIfFatal( 'some string without error' )


class TestValCastingFromApi(unittest.TestCase):


    def test_int_mapping(self):
        self.assertEqual( castValToPy( '1' ) , 1 )

    def test_yes_mapping(self):
        self.assertEqual( castValToPy( 'yes' ) , True )

    def test_no_mapping(self):
        self.assertEqual( castValToPy( 'no' ) , False )

    def test_ture_mapping(self):
        self.assertEqual( castValToPy( 'true' ) , True )

    def test_false_mapping(self):
        self.assertEqual( castValToPy( 'false' ) , False )

    def test_None_mapping(self):
        self.assertEqual( castValToPy( '' ) , None )

    def test_string_mapping(self):
        self.assertEqual( castValToPy( 'string' ) , 'string' )

    def test_float_mapping(self):
        self.assertEqual( castValToPy( '22.2' ) , '22.2' )


class TestValCastingFromPython(unittest.TestCase):


    def test_None_mapping(self):
        self.assertEqual( castValToApi( None ) , '' )

    def test_int_mapping(self):
        self.assertEqual( castValToApi( 22 ) , '22' )

    def test_float_mapping(self):
        self.assertEqual( castValToApi( 22.2 ) , '22.2' )

    def test_string_mapping(self):
        self.assertEqual( castValToApi( 'string' ) , 'string' )

    def test_True_mapping(self):
        self.assertEqual( castValToApi( True ) , 'yes' )

    def test_False_mapping(self):
        self.assertEqual( castValToApi( False ) , 'no' )



class AttributeWordConversion(unittest.TestCase):

    def test_splits_key_and_value( self ):
        api_word = convattrwrd( '=key=value' )
        self.assertEqual( api_word, ( 'key', 'value' ) )

    def test_splits_key_and_value_with_id_key( self ):
        api_word = convattrwrd( '=.id=value' )
        self.assertEqual( api_word, ( '.id', 'value' ) )



class AttributeWordCreation(unittest.TestCase):

    def test_creates_valid_api_word( self ):
        result = mkattrwrd( ( 'key', 'value' ) )
        self.assertEqual( result, '=key=value' )

    def test_creates_valid_api_word_with_id_key( self ):
        result = mkattrwrd( ( '.id', 'value' ) )
        self.assertEqual( result, '=.id=value' )



class ApiSentenceCreation(unittest.TestCase, SentenceEquality):

    def test_returns_valid_api_sentence( self ):
        self.addTypeEqualityFunc(tuple, 'assertApiSentenceEqual')
        call_dict = { 'interface':'ether1', 'disabled':'false' }
        result = ( '=interface=ether1', '=disabled=false' )
        self.assertEqual( result, mksnt( call_dict ) )


@patch('mcm.librouteros.datastructures.parsnt', return_value=())
class ApiResponseParsing(unittest.TestCase):


    def test_filters_out_empty_sentences( self, parsesnt_mock ):
        sentences = ( (), () )
        expected_result = ()
        result = parsresp( sentences )
        self.assertEqual( expected_result, result )


    def test_calls_api_sentence_parsing_method( self, parsesnt_mock ):
        sentences = ( (1,2), (1,2) )
        expected_calls = [ call(elem) for elem in sentences ]

        parsresp( sentences )
        calls = parsesnt_mock.mock_calls
        self.assertEqual( calls, expected_calls )



@patch('mcm.librouteros.datastructures.convattrwrd', return_value = (1,2))
class ApiSentenceParsing(unittest.TestCase):


    def test_calls_tuple_creation_method(self, convattr_mock):
        call_snt = ( '=disabled=false', '=interface=ether1' )

        parsnt( call_snt )
        call_list = [ call(elem) for elem in call_snt ]
        self.assertEqual( call_list, convattr_mock.mock_calls )


    def test_filters_out_non_attribute_words(self, convattr_mock):
        call_snt = ( '=disabled=false', '=interface=ether1', 'no_attr_word' )

        parsnt( call_snt )
        call_list = [ call(elem) for elem in call_snt[:2] ]
        self.assertEqual( call_list, convattr_mock.mock_calls )
