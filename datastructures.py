# -*- coding: UTF-8 -*-

class CmdPathElem:

    def __init__(self, data, keys, split_pairs):
        '''
        data
            Tuple with (key,value) tuple/s.
        keys
            Tuple with key names.
        split_pairs
            Tuple with (split_key, split_char) tuple/s.
        '''

        self.data = data
        self.keys = keys
        self.split_pairs = split_pairs

    def __str__(self):
        return ' '.join('{}={}'.format(key, value) for key, value in self.data)

    def __eq__(self, other):
        return self.data == other.data

    def __ne__(self, other):
        return self.data != other.data

    def __hash__(self):
        return hash(self.data)

    def __iter__(self):
        return iter(self.data)

    def __sub__(self, other):
        self.difference(other)

    def difference(self, other):

        difference = set(self.data) - set(other.data)

        return difference


    def strdiff( left, right, splchr ):
        '''
        Compare two strings and return items from left not present in right.
        Items from right,left are splitted by splchr and compared.
        Returns string joined by splchr. _strdiff('1,2,3','1',',') may return
        '3,2' or '2,3'.

        left
            String containing elements.
        right
            String containing elements.
        splchr
            Split character to split left and right by.
        '''

        left_splitted = left.split( splchr )
        rigth_splitted = right.split( splchr )
        diff = set( left_splitted ) - set( rigth_splitted )

        return splchr.join( diff )

