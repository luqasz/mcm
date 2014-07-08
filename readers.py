# -*- coding: UTF-8 -*-


'''
Module that holds various Printer classes. They are used to retreive rules from given menu.
'''



'''
Descriptors
'''


class CachedRead:
    '''
    Print all elements from menu and set attribute on instance.
    '''

    def __get__(self, inst, own):
        data = inst.api.run( inst.path.getall )
        data = self.filter( data )
        inst.__dict__['data'] = data
        return data

    def filter(self, data):

        return tuple( elem for elem in data if not elem.get('dynamic') )


'''
Non query enabled classes
'''


class ApiReader:

    data = CachedRead()

    def __init__(self, path, api):
        '''
        path
            menu path
        api
            api instance
        '''
        self.path = path
        self.api = api


    def get(self):

        return self.data



class WithKeyPrinter(GenericPrinter):
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

