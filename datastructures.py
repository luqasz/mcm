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

    def __init__(self, data):
        '''
        data
            Dict with read data.
        '''

        self.data = data


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
        return CmdPathElem( data=diff )


    def difference( wanted, present ):
        '''
        Return elements in wanted that are not in present.
        '''

        return dict(set(wanted.items()) - set(present.items()))
