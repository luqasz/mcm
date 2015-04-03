# -*- coding: UTF-8 -*-

from cmdpath import get_cmd_path
from datastructures import CmdPathRow



class MasterAdapter:


    def __init__(self, device):
        self.device = device


    def read(self, path):
        content = self.device.read(path.absolute)
        content = assemble_data(data=content)
        return get_cmd_path(path, data=content)



class SlaveAdapter:


    def __init__(self, device):
        self.device = device


    def read(self, path):
        content = self.device.read(path.absolute)
        content = assemble_data(data=content)
        return get_cmd_path(path, data=content)


    def write(self, path, action, data):
        for row in disassemble_data(data=data):
            self.device.write(path=path.absolute, cmd=action, data=row)





def assemble_data(data):
    return tuple(CmdPathRow(data=elem) for elem in data)


def disassemble_data(data):
    return tuple(elem.data for elem in data)
