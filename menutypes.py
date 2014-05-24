# -*- coding: UTF-8 -*-

from librouteros.extras import dictdiff



class Single:
    '''
    This class is used to compare single element menus. Such as /snmp,/system/ntp/client
    '''

    def __init__(self, printer):
        self.Printer = printer


    def compare(self, wanted):

        present = self.Printer.get()
        difference = dictdiff( wanted=wanted, present=present )
        SET = ( difference, ) if difference else tuple()

        return tuple(), SET, tuple()



class SimpleKey:
    '''
    Class for comparing menus with unique key. /queue/simple where key is 'name'.
    Items are unordered. Can not have duplicates. Only one key allowed.
    '''

    def __init__(self, printer, key, exact):
        '''
        DEL
            list with rules to delete
        SET
            list with rules to set
        ADD
            list with rules to add
        printer
            Printer object responsible for printing elements
        key
            unique key used name
        exact
            bool whether remove remaining rules or not
        '''

        self.DEL = []
        self.SET= []
        self.ADD = []
        self.Printer = printer
        self.key = key
        self.exact = exact


    def compare(self, wanted):

        for rule in wanted:
            kvp = ({ self.key : rule[self.key] },)
            present = self.Printer.get( kvp=kvp )
            difference = dictdiff( wanted=rule, present=present )
            self.decide( difference, present )

        self.purge(wanted)

        return tuple(self.DEL), tuple(self.SET), tuple(self.ADD)


    def decide(self, difference, present):

        if present.get('ID'):
            difference['ID'] = present['ID']
            self.SET.append(difference)
        else:
            self.ADD.append(difference)


    def purge(self, wanted):

        if self.exact:
            kvps = [ { self.key : rule[self.key] } for rule in wanted ]
            self.DEL.extend( self.Printer.notIn( kvp=kvps  ) )


class CompositeKey:
    '''
    Class for composite key menus. /ip/firewall/address-list where 'list' and 'address' creates a composite key.
    May have 2 or more keys as compositekey. Order is irrelevant. May have duplicates.
    '''

    def __init__(self, printer, keys, exact):
        '''
        DEL
            list with rules to delete
        SET
            list with rules to set
        ADD
            list with rules to add
        printer
            Printer object responsible for printing elements
        keys
            keys to use as composite key
        exact
            bool whether remove remaining rules or not
        '''

        self.DEL = []
        self.SET= []
        self.ADD = []
        self.Printer = printer
        self.keys = keys
        self.exact = exact


    def compare(self, wanted):

        for rule in wanted:
            compkey = dict( (key,rule[key]) for key in self.keys )
            present = self.Printer.get( kvp=compkey )
            difference = dictdiff( wanted=rule, present=present )
            self.decide( difference, present )

        self.purge(wanted)

        return tuple(self.DEL), tuple(self.SET), tuple(self.ADD)


    def decide(self, difference, present):

        if present.get('ID'):
            difference['ID'] = present['ID']
            self.SET.append(difference)
        else:
            self.ADD.append(difference)


    def purge(self, wanted):

        if self.exact:

            kvps = []
            for rule in wanted:
                compkey = dict( (key,rule[key]) for key in self.keys )
                kvps.append(compkey)

            self.DEL.extend( self.Printer.notIn( kvp=kvps ) )

