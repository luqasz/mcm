# -*- coding: UTF-8 -*-

from datastructures import CmdPathRow



class MasterAdapter:


    def __init__(self, device):
        self.device = device


    def read(self, path):
        content = self.device.read(path=path.absolute)
        return self.assemble_data(data=content)


    @staticmethod
    def assemble_data(data):
        return tuple(CmdPathRow(data=elem) for elem in data)



class SlaveAdapter(MasterAdapter):


    def write(self, path, action, data):
        for row in self.disassemble_data(data=data):
            self.device.write(path=path.absolute, action=action, data=row)


    @staticmethod
    def disassemble_data(data):
        return tuple(elem.data for elem in data)





