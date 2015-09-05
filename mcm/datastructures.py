# -*- coding: UTF-8 -*-

from posixpath import join as pjoin
from collections import namedtuple

from mcm.cmdpathtypes import MENU_PATHS


CmdPath = namedtuple('CmdPath', ('absolute', 'type', 'keys', 'modord', 'strategy'))


def make_cmdpath(path, strategy):
    attrs = dict()
    attrs['absolute'] = pjoin('/', path ).rstrip('/')
    attrs['strategy'] = strategy
    path_attrs = MENU_PATHS[path]
    attrs['keys'] = path_attrs['keys']
    attrs['type'] = path_attrs['type']
    attrs['modord'] = path_attrs['modord']

    return CmdPath(**attrs)




class CmdPathRow:

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
        bool_map = {True:'yes', False:'no'}
        return ' '.join('{}={}'.format(key, bool_map.get(value, value)) for key, value in self.data.items())


    def __eq__(self, other):
        return self.data == other.data


    def __ne__(self, other):
        return self.data != other.data


    def __bool__(self):
        return bool(self.data)


    def __hash__(self):
        return hash(tuple(self.data.items()))


    def __setitem__(self, key, value):
        self.data[key] = value


    def __getitem__(self, key):
        return self.data[key]


    def __sub__(self, other):

        diff = self.difference( wanted=self.data, present=other.data )
        return CmdPathRow( data=diff )


    def isunique(self, other, keys):

        pairs = set( (key,self[key]) for key in keys )
        return pairs <= set(other.data.items())


    @staticmethod
    def difference( wanted, present ):
        '''
        Return elements in wanted that are not in present.
        '''

        return dict(set(wanted.items()) - set(present.items()))
