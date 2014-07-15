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


