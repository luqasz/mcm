# -*- coding: UTF-8 -*-

from posixpath import join as pjoin



class MenuPath(tuple):

    __slots__ = ()

    def __new__(_cls, path, remove, set, add, getall):
        return tuple.__new__(_cls, (path, remove, set, add, getall))

    def __repr__(self):
        return 'MenuPath({!r}, remove={!r}, set={!r}, add={!r}, getall={!r})'.format(*self)

    path = property( lambda x: x[0][:-1] )
    remove = property( lambda x: x[1] )
    set = property( lambda x: x[2] )
    add = property( lambda x: x[3] )
    getall = property( lambda x: x[4] )

def mkpath( path ):

    fields = ('', 'remove', 'set', 'add', 'getall')
    attrs = tuple( pjoin( '/', path, attr ) for attr in fields )
    return MenuPath( *attrs )
