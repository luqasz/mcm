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


    def __init__(self, printer, keys):
        '''
        DEL
            list with rules to delete
        SET
            list with rules to set
        ADD
            list with rules to add
        SAVE_IDS
            list with rule IDs not to be removed
        printer
            Printer object responsible for printing elements
        keys
            key names that create unique key
        '''

        self.DEL = []
        self.SET= []
        self.ADD = []
        self.SAVE_IDS = []
        self.Printer = printer
        self.keys = keys


    def compare(self, wanted):

        present_rules = self.Printer.data

        for prule, wrule in zip_longest(present_rules, wanted, fillvalue=dict()):
            diff = dictdiff( wanted=wrule, present=prule )
            self.decide( difference=diff, present=prule )

        self.purge()


    def decide(self, difference, present):

        ID = present.get('ID')

        if ID and difference:
            difference['ID'] = ID
            self.SET.append(difference)
        elif difference:
            self.ADD.append(difference)


    def purge(self):

        pass


class SingleElementCmdPath(GenericCmdPath):
    '''
    This class is used to compare single element menus. Such as /snmp,/system/ntp/client
    '''


    def compare(self, wanted):

        present = self.Printer.get()[0]
        difference = dictdiff( wanted=wanted, present=present )
        self.SET = [difference] if difference else list()



class UniqueKeyCmdPath(GenericCmdPath):
    '''
    This class holds methods for comparing composite and single key menus.
    '''


    def compare(self, wanted):

        for rule in wanted:
            kvp = self.mkkvp( rule )
            present = self.Printer.get( kvp=kvp )
            difference = dictdiff( wanted=rule, present=present )
            self.decide( difference, present )

        self.purge()


    def mkkvp(self, elem):
        '''
        Make (extract) key,value pairs out of elem.
        '''

        return dict( (key,elem[key]) for key in self.keys )

