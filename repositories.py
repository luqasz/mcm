# -*- coding: UTF-8 -*-

from cmdpath import UniqueKeyCmdPath, OrderedCmdPath, SingleElementCmdPath


class UniqueKeyRepo:

    def read(self, device, path):

        content = device.read( path )
        return UniqueKeyCmdPath( content )

    def write(self, device, data, path):

        device.write(data, path)


class OrderedCmdRepo:

    def read(self, device, path):

        content = device.read( path )
        return OrderedCmdPath( content )

    def write(self, device, data, path):

        device.write(data, path)


class SingleCmdRepo:

    def read(self, device, path):

        content = device.read( path )
        return SingleElementCmdPath( content )

    def write(self, device, data, path):

        device.write(data, path)


def get_repository(type):

    repo_map = {'single':SingleCmdRepo, 'ordered':OrderedCmdRepo, 'uniquekey':UniqueKeyRepo}
    return repo_map[type]()
