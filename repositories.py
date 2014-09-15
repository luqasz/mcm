# -*- coding: UTF-8 -*-

from cmdpath import UniqueKeyCmdPath, OrderedCmdPath, SingleElementCmdPath
from datastructures import CmdPathElem

class GenericRepo:

    def __init__(self, class_type, keys, split_map):
        self.class_type = class_type
        self.split_map = split_map
        self.keys = keys


    def read(self, device, path):

        content = device.read( path=path )
        content = self.assembleData(data=content)
        return self.class_type(data=content)


    def write(self, device, data, path):

        content = self.disassembleData(data=data)
        device.write(data=content, path=path)


    def assembleData(self, data):

        return [CmdPathElem(data=elem, keys=self.keys, split_map=self.split_map) for elem in data]


    def disassembleData(self, data):

        return [elem.data for elem in data]



class UniqueKeyRepo(GenericRepo):

    def __init__(self, class_type, keys, split_map):
        self.class_type = class_type
        self.split_map = split_map
        self.keys = keys



class OrderedCmdRepo(GenericRepo):


    def __init__(self, class_type, keys, split_map):
        self.class_type = class_type
        self.split_map = split_map
        self.keys = tuple()



class SingleCmdRepo(GenericRepo):


    def __init__(self, class_type, keys, split_map):
        self.class_type = class_type
        self.split_map = split_map
        self.keys = tuple()




def get_repository(type, keys, split_map):

    repo_map = {'single':SingleCmdRepo, 'ordered':OrderedCmdRepo, 'uniquekey':UniqueKeyRepo}
    cmdpath_map = {'single':SingleElementCmdPath, 'ordered':OrderedCmdPath, 'uniquekey':UniqueKeyCmdPath}
    cls = repo_map[type]
    cls_type = cmdpath_map[type]
    return cls(class_type=cls_type, keys=keys, split_map=split_map)
