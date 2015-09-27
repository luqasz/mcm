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



class CmdPathRow(dict):


    def __str__(self):
        bool_map = {True:'yes', False:'no', None:'""', '':'""'}
        return ' '.join('{}={}'.format(key, bool_map.get(value, value)) for key, value in self.items())


    def __hash__(self):
        return hash(tuple(self.items()))


    def __sub__(self, other):
        '''Return new instance with key,valie pairs from self not listed in other.'''

        diff = dict(set(self.items()) - set(other.items()))
        return CmdPathRow( diff )


    def isunique(self, other, keys):
        '''Test whether every key,value pair (from keys) is in other.'''

        pairs = set( (key,self[key]) for key in keys )
        return pairs <= set(other.items())
