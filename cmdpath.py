# -*- coding: UTF-8 -*-

from itertools import zip_longest

from datastructures import CmdPathRow



def get_cmd_path(path, data):
    if path.type == 'single':
        return SingleElementCmdPath(data=data)
    elif path.type == 'ordered':
        return OrderedCmdPath(data=data)
    elif path.type == 'uniquekey':
        return UniqueKeyCmdPath(data=data, keys=path.keys)


class GenericCmdPath:

    def __iter__(self):
        return iter(self.data)


class OrderedCmdPath(GenericCmdPath):


    def __init__(self, data):

        self.DEL = []
        self.SET= []
        self.ADD = []
        self.data = data


    def decide(self, wanted, difference, present):

        if wanted and difference and not present:
            self.ADD.append( wanted )
        elif not wanted and not difference and present:
            self.DEL.append( present )
        elif wanted and difference and present:
            difference['ID'] = present['ID']
            self.SET.append( difference )


    def compare(self, wanted):

        fillval = CmdPathRow(data=dict())
        for wanted_rule, present_rule in zip_longest(wanted, self, fillvalue=fillval):
            diff = wanted_rule - present_rule
            self.decide(wanted_rule, diff, present_rule)

        return tuple(self.ADD), tuple(self.SET), tuple(self.DEL)



class SingleElementCmdPath(GenericCmdPath):


    def __init__(self, data):
        self.data = data


    def compare(self, wanted):
        for wanted_row, present_row in zip(wanted, self):
            diff = wanted_row - present_row
            SET = (diff,) if diff else tuple()

        return tuple(), SET, tuple()



class UniqueKeyCmdPath(GenericCmdPath):


    def __init__(self, data, keys):

        self.data = data
        self.keys = keys
        self.SET = []
        self.ADD = []
        self.NO_DELETE = []


    def compare(self, wanted):

        for wanted_rule in wanted:
            present_rule = self.findPair(searched=wanted_rule)
            diff = wanted_rule - present_rule
            self.decide(wanted_rule, diff, present_rule)

        DEL = set(self.data) - set(self.NO_DELETE)
        return tuple(self.ADD), tuple(self.SET), tuple(DEL)


    def decide(self, wanted, difference, present):

        if wanted and difference and not present:
            self.ADD.append( wanted )
        elif wanted and difference and present:
            self.NO_DELETE.append(present)
            difference['ID'] = present['ID']
            self.SET.append( difference )
        elif wanted and not difference and present:
            self.NO_DELETE.append(present)


    def findPair(self, searched):

        for row in self:
            if row.isunique(other=searched, keys=self.keys):
                return row
        else:
            return CmdPathRow(data=dict())
