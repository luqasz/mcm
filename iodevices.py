# -*- coding: UTF-8 -*-

from posixpath import join as pjoin



class StaticConfig:


    def __init__(self, data):
        self.data = data


    def read(self, path):
        for searched_path, rules in self.data.items():
            if searched_path.absolute == path:
                return rules



class RouterOsAPIDevice:


    def __init__(self, api):
        self.api = api


    def read(self, path):
        cmd = cmd_action_join(path=path, action='GET')
        data = self.api.run(cmd=cmd)
        return filter_dynamic(data)


    def write(self, path, action, data):
        command = cmd_action_join(path=path, action=action)
        method = getattr(self, action)
        method(command=command, data=data)


    def DEL(self, command, data):
        ID = {'ID':data['ID']}
        self.api.run(cmd=command, args=ID)


    def SET(self, command, data):
        self.api.run(cmd=command, args=data)


    def ADD(self, command, data):
        self.api.run(cmd=command, args=data)




def cmd_action_join(path, action):
    actions = dict(ADD='add', SET='set', DEL='remove', GET='getall')
    return pjoin(path, actions[action])


def filter_dynamic(data):
    return tuple(row for row in data if not row.get('dynamic'))
