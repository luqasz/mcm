# -*- coding: UTF-8 -*-

from comparators import get_comparator
from datastructures import CmdPathRow



class MasterAdapter:


    def __init__(self, device):
        self.device = device


    def read(self, path):
        content = self.device.read(path.absolute)
        content = assemble_data(data=content)
        return get_comparator(path, data=content)



class SlaveAdapter(MasterAdapter):


    def write(self, path, action, data):
        for row in disassemble_data(data=data):
            self.device.write(path=path.absolute, cmd=action, data=row)





def assemble_data(data):
    return tuple(CmdPathRow(data=elem) for elem in data)


def disassemble_data(data):
    return tuple(elem.data for elem in data)
