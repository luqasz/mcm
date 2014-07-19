# -*- coding: UTF-8 -*-

from librouteros.extras import dictdiff

from itertools import zip_longest
from posixpath import join as pjoin
from collections import namedtuple


CmdPath = namedtuple('CmdPath', ('path', 'remove', 'set', 'add', 'getall', 'type', 'modord', 'keys', 'split_by', 'split_keys') )


def mkCmdPath( path, attrs ):

    fields = ('remove', 'set', 'add', 'getall')
    field_attrs = ( pjoin('/', path), )
    field_attrs += tuple( pjoin( '/', path, attr ) for attr in fields )
    return CmdPath( *field_attrs, **attrs )



class GenericCmdPath:


    def __init__(self, data, keys):
        '''
        DEL
            list with rules to delete
        SET
            List with rules to set. Each element is a tuple (present,difference)
        ADD
            list with rules to add
        data
            Read previously data for given cmd path
        keys
            key names that create unique key
        '''

        self.DEL = []
        self.SET= []
        self.ADD = []
        self.data = data
        self.keys = keys


    def decide(self, difference, present):

        ID = present.get('ID')
        diff = dict(difference)
        pres = dict(present)

        if ID and difference:
            diff['ID'] = ID
            pair = ( pres, diff )
            self.SET.append(pair)
        elif difference:
            self.ADD.append(diff)


    def populateDEL(self):

        saved = ( elem[0] for elem in self.SET )
        self.DEL = list( elem for elem in self.data if elem not in saved )



class OrderedCmdPath(GenericCmdPath):
    '''
    This class is used to compare ordered command paths. Such as /ip/firewall/filter
    '''


    def compare(self, wanted):

        for prule, wrule in zip_longest(self.data, wanted, fillvalue=dict()):
            diff = dictdiff( wanted=wrule, present=prule )
            self.decide( difference=diff, present=prule )

        self.populateDEL()


class SingleElementCmdPath(GenericCmdPath):
    '''
    This class is used to compare single element menus. Such as /snmp,/system/ntp/client
    '''


    def compare(self, wanted):

        wanted = wanted[0]
        present = self.data[0]
        difference = dictdiff( wanted=wanted, present=present )
        self.SET = [(present,difference)] if difference else list()



class UniqueKeyCmdPath(GenericCmdPath):
    '''
    This class holds methods for comparing composite and single key menus.
    '''


    def compare(self, wanted):

        for rule in wanted:
            kvp = self.mkkvp( rule )
            present = self.search( kvp )
            difference = dictdiff( wanted=rule, present=present )
            self.decide( difference, present )

        self.populateDEL()


    def mkkvp(self, elem):
        '''
        Make (extract) key,value pairs out of elem.
        '''

        return dict( (key,elem[key]) for key in self.keys )


    def search(self, kvp):
        '''
        Return first found key value pair/s. Duplicates are ignored.

        kvp
            dictionary with key, value pairs
        '''

        # prepare function call
        func = lambda rule: self.issubset( kvp, rule )
        for found in filter( func, self.data ):
            return found
        else:
            return dict()


    def issubset(self, kvp, rule):
        '''
        Check if all key, value pairs from kvp are in rule.
        '''

        return set(kvp.items()) <= set(rule.items())
