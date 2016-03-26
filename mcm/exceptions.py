# -*- coding: UTF-8 -*-


class ValidateError(Exception):
    '''
    Exception raised when a general validation error occurs.
    '''


class ParseError(Exception):
    '''
    Exception raised when parsing configuration fails.
    '''


class ReadError(Exception):
    '''
    Exception raised when reading from master or slave occured.
    '''


class WriteError(Exception):
    '''
    Exception raised when writing to master or slave occured.
    '''
