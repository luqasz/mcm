# -*- coding: UTF-8 -*-

class CmdPathElem:

    def __init__(self, data, keys=tuple(), split_map=dict()):
        '''
        data
            Dict with read data.
        keys
            Tuple with key names.
        split_map
            Dictionary with split_key, split_char.
        '''

        self.data = data
        self.keys = keys
        self.split_map = split_map


    def __str__(self):
        '''
        Return nicelly formated code. Usefull for logging.
        '''

        return ' '.join('{}={}'.format(key, value) for key, value in self.data.items())


    def __eq__(self, other):
        '''
        other
            CmdPathElem instance
        '''
        return self.data == other.data


    def __ne__(self, other):
        '''
        other
            CmdPathElem instance
        '''
        return self.data != other.data


    def __iter__(self):
        return self.data.items()


    def __getitem__(self, key):

        return self.data[key]

    def __sub__(self, other):
        '''
        Return a new CmdPathElem with elements in self that are not in other.

        other
            CmdPathElem instance
        '''

        diff = CmdPathElem.difference( wanted=self.data, present=other.data, split_map=self.split_map )
        return CmdPathElem( data=diff, keys=self.keys, split_map=self.split_map )


    def difference( wanted, present, split_map=dict() ):
        '''
        Return elements in wanted that are not in present. Additional comparison is made using split_map.
        '''

        diff = dict(set(wanted.items()) - set(present.items()))

        for split_key, split_char in split_map.items():
            if diff.get(split_key) and present.get(split_key):
                diff[split_key] = CmdPathElem.strdiff( diff[split_key], present[split_key], split_char )

        return diff


    def strdiff( wanted, present, splchr ):
        '''
        Compare two strings and return items from wanted not present in present.
        Items from present,wanted are splitted by splchr and compared.
        Returns string joined by splchr. strdiff('1,2,3','1',',') may return
        '3,2' or '2,3'.

        wanted
            String containing elements.
        present
            String containing elements.
        splchr
            Split character to split wanted and present by.
        '''

        wanted_splitted = wanted.split( splchr )
        present_splitted = present.split( splchr )
        diff = set( wanted_splitted ) - set( present_splitted )

        return splchr.join( diff )

