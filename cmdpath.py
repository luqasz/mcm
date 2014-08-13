# -*- coding: UTF-8 -*-

from itertools import zip_longest
from posixpath import join as pjoin
from collections import namedtuple

from datastructures import CmdPathElem

CmdPath = namedtuple('CmdPath', ('path', 'remove', 'set', 'add', 'getall', 'type', 'modord', 'keys', 'split_by', 'split_keys') )


def mkCmdPath( path, attrs ):

    fields = ('remove', 'set', 'add', 'getall')
    field_attrs = ( pjoin('/', path), )
    field_attrs += tuple( pjoin( '/', path, attr ) for attr in fields )
    return CmdPath( *field_attrs, **attrs )



class GenericCmdPath:


    def __init__(self, data):
        '''
        DEL
            list with rules to delete
        SET
            List with rules to set. Each element is a tuple (present,difference)
        ADD
            list with rules to add
        data
            Read previously data for given cmd path
        '''

        self.DEL = []
        self.SET= []
        self.ADD = []
        self.data = data


    def decide(self, difference, present):

        if difference and not present:
            self.ADD.append( difference )
        elif present and not difference:
            self.DEL.append( present )
        elif present and difference:
            try:
                difference['ID'] = present['ID']
            except KeyError:
                pass
            finally:
                self.SET.append( (present, difference) )


    def populateDEL(self):
        '''
        Add rows from self.data that are not present in saved. That is they were not added to SET by decide method.
        '''

        saved = tuple( elem[0] for elem in self.SET )
        for row in self.data:
            if row in saved:
                self.DEL.append( row )


class OrderedCmdPath(GenericCmdPath):
    '''
    This class is used to compare ordered command paths. Such as /ip/firewall/filter
    '''


    def compare(self, wanted):

        fillobj = CmdPathElem( data=dict(), keys=tuple(), split_map=dict() )
        for prule, wrule in zip_longest(self.data, wanted, fillvalue=fillobj):
            diff = wrule - prule
            self.decide( difference=diff, present=prule )

        self.populateDEL()
        return self.ADD, self.SET, self.DEL


class SingleElementCmdPath(GenericCmdPath):
    '''
    This class is used to compare single element menus. Such as /snmp,/system/ntp/client
    '''


    def compare(self, wanted):

        wanted = wanted[0]
        present = self.data[0]
        difference = wanted - present
        self.decide( difference, present )

        return self.ADD, self.SET, self.DEL



class UniqueKeyCmdPath(GenericCmdPath):
    '''
    This class holds methods for comparing unique key,value command paths.
    '''


    def compare(self, wanted):

        for rule in wanted:
            found = self.search( rule )
            difference = rule - found
            self.decide( difference, found )

        self.populateDEL()

        return self.ADD, self.SET, self.DEL


    def search(self, rule):
        '''
        Return first found item in self that is unique to rule.
        '''

        for elem in self.data:
            if elem.isunique( rule ):
                return elem
        else:
            return CmdPathElem( data=dict(), keys=tuple(), split_map=dict() )
