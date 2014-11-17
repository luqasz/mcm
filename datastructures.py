# -*- coding: UTF-8 -*-

from posixpath import join as pjoin



class CmdPath:


    def __init__(self, base):
        self.base = pjoin('/', base ).rstrip('/')
        self.cmd = None
        self.remove = pjoin('/', self.base, 'remove')
        self.add = pjoin('/', self.base, 'add')
        self.set = pjoin('/', self.base, 'set')
        self.getall = pjoin('/', self.base, 'getall')



class CmdPathElem:

    def __init__(self, data, keys=tuple()):
        '''
        data
            Dict with read data.
        keys
            Tuple with key names.
        '''

        self.data = data
        self.keys = keys


    def isunique(self, other):
        '''
        Test whether self is a Unique rule. That is all self.keys and their values are in other.
        '''

        pairs = set( (key,self[key]) for key in self.keys )
        return pairs <= set(other.data.items())


    def __str__(self):
        '''
        Return ready for logging data.
        '''

        return ' '.join('{}={}'.format(key, value) for key, value in self.data.items())


    def __eq__(self, other):
        '''
        other
            CmdPathElem instance
        '''
        return self.data == other.data


    def __ne__(self, other):
        '''
        other
            CmdPathElem instance
        '''
        return self.data != other.data


    def __bool__(self):
        return bool(self.data)


    def __setitem__(self, key, value):
        self.data[key] = value


    def __getitem__(self, key):

        return self.data[key]


    def __sub__(self, other):
        '''
        Return a new CmdPathElem with elements in self that are not in other.

        other
            CmdPathElem instance
        '''

        diff = CmdPathElem.difference( wanted=self.data, present=other.data )
        return CmdPathElem( data=diff, keys=self.keys )


    def difference( wanted, present ):
        '''
        Return elements in wanted that are not in present.
        '''

        return dict(set(wanted.items()) - set(present.items()))


    def strdiff( wanted, present, splchr ):
        '''
        Compare two strings and return items from wanted not present in present.
        Items from present,wanted are splitted by splchr and compared.
        Returns string joined by splchr. strdiff('1,2,3','1',',') may return
        '3,2' or '2,3'.

        wanted
            String containing elements.
        present
            String containing elements.
        splchr
            Split character to split wanted and present by.
        '''

        wanted_splitted = wanted.split( splchr )
        present_splitted = present.split( splchr )
        diff = set( wanted_splitted ) - set( present_splitted )

        return splchr.join( diff )

