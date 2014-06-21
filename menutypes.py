# -*- coding: UTF-8 -*-

from librouteros.extras import dictdiff

from itertools import zip_longest


class GenericMenu:


    def __init__(self, printer, keys, exact):
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
        exact
            bool whether remove remaining rules or not
        '''

        self.DEL = []
        self.SET= []
        self.ADD = []
        self.SAVE_IDS = []
        self.Printer = printer
        self.keys = keys
        self.exact = exact


    def compare(self, wanted):

        present_rules = self.Printer.get()

        for prule, wrule in zip_longest(present_rules, wanted, fillvalue=dict()):
            diff = dictdiff( wanted=wrule, present=prule )
            self.decide( difference=diff, present=prule )
            self.saveDecide( prule )

        self.purge()
        return tuple(self.DEL), tuple(self.SET), tuple(self.ADD)


    def decide(self, difference, present):

        ID = present.get('ID')

        if ID and difference:
            difference['ID'] = ID
            self.SET.append(difference)
        elif difference:
            self.ADD.append(difference)


    def saveDecide(self, present):

        try:
            self.SAVE_IDS.append( present['ID'] )
        except KeyError:
            pass


    def purge(self):

        if self.exact:
            self.DEL = self.Printer.exceptIDs( ids=self.SAVE_IDS )



class SingleMenu(GenericMenu):
    '''
    This class is used to compare single element menus. Such as /snmp,/system/ntp/client
    '''


    def compare(self, wanted):

        present = self.Printer.get()[0]
        difference = dictdiff( wanted=wanted, present=present )
        SET = ( difference, ) if difference else tuple()
        return tuple(), SET, tuple()



class WithKeyMenu(GenericMenu):
    '''
    This class holds methods for comparing composite and single key menus.
    '''


    def compare(self, wanted):

        for rule in wanted:
            kvp = self.mkkvp( rule )
            present = self.Printer.get( kvp=kvp )
            difference = dictdiff( wanted=rule, present=present )
            self.decide( difference, present )
            self.saveDecide( present )

        self.purge()
        return tuple(self.DEL), tuple(self.SET), tuple(self.ADD)


    def mkkvp(self, elem):
        '''
        Make (extract) key,value pairs out of elem.
        '''

        return dict( (key,elem[key]) for key in self.keys )

