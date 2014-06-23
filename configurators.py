# -*- coding: UTF-8 -*-

'''
Module that holds configuration classes and helpers.
'''



class GenericConfigurator:


    def __init__(self, api, log):
        self.api = api
        self.log = log


    def applyMenu(self, rules, menu_type, modord, path):
        '''
        rules:
            iterable with dictionaries as rules
        menu_type:
            instantiated MenuType object
        modord:
            iterable with modification order as string
        path:
            MenuPath namedtuple
        '''

        DEL, SET, ADD = menu_type.compare( rules )
        data_action_map = {'DEL':DEL, 'SET':SET, 'ADD':ADD}
        for action in modord:
            method = getattr( self, action )
            method( data_action_map[action], path )


class NonQueriedConfigurator(GenericConfigurator):
    '''
    Class with methods for non query enabled routeros devices.
    '''


    def ADD(self, rules, path):

        for elem in rules:
            self.api.run( path.add, elem )


    def SET(self, rules, path):

        for elem in rules:
            self.api.run( path.set, elem )


    def DEL(self, rules, path):

        for elem in rules:
            self.api.run( path.remove, elem )


class DryRunConfigurator(GenericConfigurator):
    '''
    Class for dummy/dry run configuration run.
    Simply just log what would be done.
    '''


    def ADD(self, rules, path):

        for elem in rules:
            self.log.info( path.add, elem )


    def SET(self, rules, path):

        for elem in rules:
            self.log.info( path.set, elem )


    def DEL(self, rules, path):

        for elem in rules:
            self.log.info( path.remove, elem )
