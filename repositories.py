# -*- coding: UTF-8 -*-

from cmdpath import UniqueKeyCmdPath, OrderedCmdPath, SingleElementCmdPath


class UniqueKeyRepo:


    def __init__(self, keys, split_map):
        self.split_map = split_map
        self.keys = keys

    def read(self, device, path):

        content = device.read( path=path )
        return UniqueKeyCmdPath( data=content )


    def write(self, device, data, path):

        device.write(data=data, path=path)



class OrderedCmdRepo:


    def __init__(self, keys, split_map):
        self.split_map = split_map


    def read(self, device, path):

        content = device.read( path=path )
        return OrderedCmdPath( data=content )


    def write(self, device, data, path):

        device.write(data=data, path=path)



class SingleCmdRepo:


    def __init__(self, keys, split_map):
        self.split_map = split_map


    def read(self, device, path):

        content = device.read( path=path )
        return SingleElementCmdPath( data=content )


    def write(self, device, data, path):

        device.write(data=data, path=path)



def get_repository(type, keys, split_map):

    repo_map = {'single':SingleCmdRepo, 'ordered':OrderedCmdRepo, 'uniquekey':UniqueKeyRepo}
    return repo_map[type](keys=keys, split_map=split_map)
