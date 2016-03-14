# -*- coding: UTF-8 -*-

from posixpath import join as pjoin

from mcm.librouteros.exceptions import TrapError, MultiTrapError


class Parser:

    api_mapping = {'yes': True, 'true': True, 'no': False, 'false': False, '': None}

    @staticmethod
    def apiCast(value: str) -> bool:
        '''
        Cast value from API to python.

        :returns: Python equivalent.
        '''
        try:
            casted = int(value)
        except ValueError:
            casted = Parser.api_mapping.get(value, value)
        return casted

    @staticmethod
    def parseWord(word: str) -> tuple:
        '''
        Values are automaticly casted to python equivalents.

        :param word: API word.
        :returns: Key, value pair.
        '''
        index_map = {'.': 0, '=': 1}
        index = index_map[word[0]]
        splited = word.split('=', index+1)
        value = Parser.apiCast(splited[index+1])
        return (splited[index], value)

    @staticmethod
    def parseWords(words: tuple) -> tuple:
        '''
        Parse each word.

        :param sentence: Read sentence.
        :returns: Tag, parsed words as dict.
        '''
        parsed = dict(Parser.parseWord(word) for word in words)
        tag = parsed.pop('.tag', None)
        return tag, parsed


class Composer:

    python_mapping = {True: 'yes', False: 'no', None: ''}

    @staticmethod
    def pythonCast(value) -> str:
        '''
        Cast value from python to API.

        :returns: Casted to API equivalent.
        '''

        # this is necesary because 1 == True, 0 == False
        if type(value) == int:
            return str(value)
        else:
            return Composer.python_mapping.get(value, str(value))

    @staticmethod
    def composeAttributeWords(pairs: tuple) -> tuple:
        '''
        Create attribute words from key, value pairs.
        Values from pairs will be casted to API quivalents.

        :param pairs: Key, value pairs.
        :returns: Attribute words.
        '''

        return tuple('=' + key + '=' + Composer.pythonCast(value) for key, value in pairs)


class Api(Composer, Parser):

    def __init__(self, protocol):
        self.protocol = protocol

    def __call__(self, cmd: str, **kwargs) -> tuple:
        '''
        Call Api with given command.

        :param cmd: Command word. eg. /ip/address/print
        :param kwargs: Optional arguments.
        '''
        words = self.composeAttributeWords(kwargs.items())
        self.protocol.writeSentence(cmd, *words)
        return self._readResponse()

    def _readSentence(self) -> tuple:
        '''
        Read one sentence and parse words.

        :returns: Reply word, tag, dict with attribute words.
        '''
        reply_word, words = self.protocol.readSentence()
        tag, words = self.parseWords(words)
        return reply_word, tag, words

    def _readResponse(self) -> tuple:
        '''
        Read untill !done is received.

        :throws TrapError: If one !trap is received.
        :throws MultiTrapError: If > 1 !trap is received.
        :returns: Full response
        '''
        response = []
        reply_word = None
        while reply_word != '!done':
            reply_word, tag, words = self._readSentence()
            response.append((reply_word, words))

        self._trapCheck(response)
        # Remove empty sentences
        return tuple(words for reply_word, words in response if words)

    def close(self):
        self.protocol.close()

    @staticmethod
    def _trapCheck(response):
        traps = tuple(words for reply_word, words in response if reply_word == '!trap')
        if len(traps) > 1:
            raise MultiTrapError(*traps)
        elif len(traps) == 1:
            trap = traps[0]
            raise TrapError(message=trap['message'], category=trap.get('category'))

    @staticmethod
    def joinPath(*path: str) -> str:
        '''
        Join two or more paths forming a command word.
        >>> api.joinPath('/ip', 'address', 'print')
        >>> '/ip/address/print'
        '''
        return pjoin('/', *path).rstrip('/')
