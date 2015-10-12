# -*- coding: UTF-8 -*-

class LibError( Exception ):
    '''
    This is a base exception for all other.
    '''


class LoginError( LibError ):
    '''
    Login attempt errors.
    '''


class CmdError( LibError ):
    '''
    Commend execution errors.
    '''


class ConnError( LibError ):
    '''
    Connection related errors.
    '''


class FatalError(LibError):
    '''
    Exception raised when !fatal is received.
    '''

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return str(self.message)


class TrapError(LibError):
    '''
    Exception raised when !trap is received.

    :param int category: Optional integer representing category.
    :param int tag: Optional associated .tag API attribute word.
    :param str message: Error message.
    '''

    def __init__(self, message, category=None, tag=None):
        self.category = category
        self.tag = tag
        self.message = message

    def __str__(self):
        return str(self.message)
