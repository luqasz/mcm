# -*- coding: UTF-8 -*-

from cmdpath import UniqueKeyCmdPath, OrderedCmdPath, SingleElementCmdPath


class UniqueKeyRepo:

    def read(self, device, path):

        content = device.read( path=path )
        return UniqueKeyCmdPath( data=content )

    def write(self, device, data, path):

        device.write(data=data, path=path)


class OrderedCmdRepo:

    def read(self, device, path):

        content = device.read( path=path )
        return OrderedCmdPath( data=content )

    def write(self, device, data, path):

        device.write(data=data, path=path)


class SingleCmdRepo:

    def read(self, device, path):

        content = device.read( path=path )
        return SingleElementCmdPath( data=content )

    def write(self, device, data, path):

        device.write(data=data, path=path)


def get_repository(type):

    repo_map = {'single':SingleCmdRepo, 'ordered':OrderedCmdRepo, 'uniquekey':UniqueKeyRepo}
    return repo_map[type]()
