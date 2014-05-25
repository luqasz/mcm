# -*- coding: UTF-8 -*-


'''
Module that holds various Printer classes. They are used to retreive rules from given menu.
'''

from posixpath import join as pjoin



'''
Descriptors
'''


class CachedPrint:
    '''
    Print all elements from menu and set attribute on instance.
    '''

    def __get__(self, inst, own):
        path = pjoin( inst.lvl, 'print' )
        data = inst.api.run( path )
        data = self.filter( data )
        inst.__dict__['data'] = data
        return data

    def filter(self, data):

        return tuple( elem for elem in data if not elem.get('dynamic') )


'''
Non query enabled classes
'''


class Generic:
    '''
    Base class for all others.
    '''

    data = CachedPrint()

    def __init__(self, lvl, api):
        '''
        lvl
            menu level
        api
            api instance
        '''
        self.lvl = lvl
        self.api = api


class Single(Generic):
    '''
    Class for single menu levels. /snmp, /system/ntp/client.
    '''


    def get(self):

        return self.data[0]


class Keyed(Generic):
    '''
    Class for menu types with composite and simple keys.
    '''

    def get(self, kvp):
        '''
        Always get first found element. Duplicates are ignored.

        kvp
            dictionary with key, value pairs
        '''

        # prepare function call
        func = lambda x: self.issubset( kvp, x )
        for found in filter( func, self.data ):
            return found
        else:
            return dict()

    def issubset(self, kvp, rule):
        '''
        Check if all key, value pairs from kvp are in rule.
        '''

        return set(kvp.items()) <= set(rule.items())

