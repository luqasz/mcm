# -*- coding: UTF-8 -*-

import unittest
try:
    from unittest.mock import MagicMock, patch, call
except ImportError:
    from mock import MagicMock, patch, call

from librouteros.datastructures import parsresp, parsnt, mksnt, mkattrwrd, convattrwrd, castValToPy, castValToApi, raiseIfFatal, trapCheck
from librouteros.exc import CmdError, ConnError



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



class ApiSentenceCreation(unittest.TestCase):

    def test_returns_valid_api_sentence( self ):
        call_dict = { 'interface':'ether1', 'disabled':'false' }
        result = ( '=interface=ether1', '=disabled=false' )
        self.assertEqual( result, mksnt( call_dict ) )



class ApiResponseParsing(unittest.TestCase):


    def setUp(self):
        parsnt_patcher = patch('librouteros.datastructures.parsnt')
        self.parsnt_mock = parsnt_patcher.start()
        self.parsnt_mock.return_value = ()
        self.addCleanup(parsnt_patcher.stop)


    def test_filters_out_empty_sentences( self ):
        sentences = ( (), () )
        expected_result = ()
        result = parsresp( sentences )
        self.assertEqual( expected_result, result )


    def test_calls_api_sentence_parsing_method( self ):
        sentences = ( (1,2), (1,2) )
        expected_calls = [ call(elem) for elem in sentences ]

        parsresp( sentences )
        calls = self.parsnt_mock.mock_calls
        self.assertEqual( calls, expected_calls )



class ApiSentenceParsing(unittest.TestCase):


    def setUp(self):
        conv_patcher = patch('librouteros.datastructures.convattrwrd')
        self.conv_mock = conv_patcher.start()
        self.conv_mock.return_value = (1,2)
        self.addCleanup(conv_patcher.stop)


    def test_calls_tuple_creation_method(self):
        call_snt = ( '=disabled=false', '=interface=ether1' )

        parsnt( call_snt )
        call_list = [ call(elem) for elem in call_snt ]
        self.assertEqual( call_list, self.conv_mock.mock_calls )


    def test_filters_out_non_attribute_words(self):
        call_snt = ( '=disabled=false', '=interface=ether1', 'no_attr_word' )

        parsnt( call_snt )
        call_list = [ call(elem) for elem in call_snt[:2] ]
        self.assertEqual( call_list, self.conv_mock.mock_calls )
