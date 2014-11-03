# -*- coding: UTF-8 -*-


class JsonFileConfig:


    def __init__(self, file):
        self.file = file


    def read(self, path):
        pass


    def write(self, data, path):
        raise NotImplementedError



class RouterOsAPIDevice:


    def __init__(self, api):
        self.api = api


    def read(self, path):
        return self.api.run(cmd=path.cmd)


    def write(self, data, path):
        self.api.run(cmd=path.cmd, args=data)
