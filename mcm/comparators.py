# -*- coding: UTF-8 -*-

from itertools import zip_longest

from mcm.datastructures import CmdPathRow



def get_comparator(path):
    if path.type == 'single':
        return SingleElementComparator()
    elif path.type == 'ordered':
        return OrderedComparator()
    elif path.type == 'uniquekey':
        return UniqueKeyComparator(keys=path.keys)



class OrderedComparator:


    def __init__(self):

        self.DEL = []
        self.SET= []
        self.ADD = []


    def decide(self, wanted, difference, present):

        if wanted and difference and not present:
            self.ADD.append( wanted )
        elif not wanted and not difference and present:
            self.DEL.append( present )
        elif wanted and difference and present:
            difference['.id'] = present['.id']
            self.SET.append( difference )


    def compare(self, wanted, present):

        fillval = CmdPathRow(dict())
        for wanted_rule, present_rule in zip_longest(wanted, present, fillvalue=fillval):
            diff = wanted_rule - present_rule
            self.decide(wanted_rule, diff, present_rule)

        return tuple(self.ADD), tuple(self.SET), tuple(self.DEL)



class SingleElementComparator:


    def compare(self, wanted, present):
        SET = tuple()
        for wanted_row, present_row in zip(wanted, present):
            diff = wanted_row - present_row
            SET = (diff,) if diff else tuple()

        return tuple(), SET, tuple()



class UniqueKeyComparator:


    def __init__(self, keys):

        self.keys = keys
        self.SET = []
        self.ADD = []
        self.NO_DELETE = []


    def compare(self, wanted, present):

        for wanted_rule in wanted:
            present_rule = self.findPair(searched=wanted_rule, present=present)
            diff = wanted_rule - present_rule
            self.decide(wanted_rule, diff, present_rule)

        DEL = set(present) - set(self.NO_DELETE)
        return tuple(self.ADD), tuple(self.SET), tuple(DEL)


    def decide(self, wanted, difference, present):

        if wanted and difference and not present:
            self.ADD.append( wanted )
        elif wanted and difference and present:
            self.NO_DELETE.append(present)
            difference['.id'] = present['.id']
            self.SET.append( difference )
        elif wanted and not difference and present:
            self.NO_DELETE.append(present)


    def findPair(self, searched, present):

        for row in present:
            if row.isunique(other=searched, keys=self.keys):
                return row
        else:
            return CmdPathRow(dict())
