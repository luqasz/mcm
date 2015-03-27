# -*- coding: UTF-8 -*-

from posixpath import join as pjoin



class StaticConfig:


    def __init__(self, data):
        self.data = data


    def read(self, path):
        return self.data[path]



class RouterOsAPIDevice:


    def __init__(self, api):
        self.api = api


    def read(self, path):
        cmd = cmd_action_join(path=path.absolute, action='GET')
        data = self.api.run(cmd=cmd)
        return filter_dynamic(data)


    def write(self, path, cmd, data):
        command = cmd_action_join(path=path.absolute, action=cmd)
        self.api.run(cmd=command, args=data)




def cmd_action_join(path, action):
    actions = dict(ADD='add', SET='set', DEL='remove', GET='getall')
    return pjoin(path, actions[action])


def filter_dynamic(data):
    return tuple(row for row in data if not row.get('dynamic'))
