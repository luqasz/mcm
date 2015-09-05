# -*- coding: UTF-8 -*-

from posixpath import join as pjoin

from mcm.librouteros import CmdError
from mcm.exceptions import ReadError, WriteError



class StaticConfig:


    def __init__(self, data):
        self.data = data


    def read(self, path):
        for section in self.data:
            if section['path'] == path:
                return section['rules']


    def close(self):
        pass



class RouterOsAPIDevice:


    def __init__(self, api):
        self.api = api


    def read(self, path):
        cmd = self.cmd_action_join(path=path, action='GET')
        try:
            data = self.api.run(cmd=cmd)
        except CmdError as error:
            raise ReadError(error)
        return self.filter_dynamic(data)


    def write(self, path, action, data):
        command = self.cmd_action_join(path=path, action=action)
        method = getattr(self, action)
        method(command=command, data=data)


    def DEL(self, command, data):
        ID = {'.id':data['.id']}
        try:
            self.api.run(cmd=command, args=ID)
        except CmdError as error:
            raise WriteError(error)


    def SET(self, command, data):
        try:
            self.api.run(cmd=command, args=data)
        except CmdError as error:
            raise WriteError(error)


    def ADD(self, command, data):
        try:
            self.api.run(cmd=command, args=data)
        except CmdError as error:
            raise WriteError(error)


    def close(self):
        self.api.close()


    @staticmethod
    def cmd_action_join(path, action):
        actions = dict(ADD='add', SET='set', DEL='remove', GET='getall')
        return pjoin(path, actions[action])


    @staticmethod
    def filter_dynamic(data):
        return tuple(row for row in data if not row.get('dynamic'))



