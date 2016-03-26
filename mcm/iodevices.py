# -*- coding: UTF-8 -*-

from logging import getLogger
from mcm.librouteros import TrapError, MultiTrapError
from mcm.exceptions import ReadError, WriteError
from mcm.datastructures import CmdPathRow

logger = getLogger('mcm.' + __name__)


class StaticConfig:

    def __init__(self, data):
        self.data = data

    def read(self, path):
        for section in self.data:
            if section['path'] == path.absolute:
                return tuple(CmdPathRow(row) for row in section['rules'])

    def close(self):
        pass


class RO_RouterOs:
    '''
    Read only RouterOs.
    '''

    actions = dict(ADD='add', SET='set', DEL='remove', GET='getall')

    def __init__(self, api):
        self.api = api

    def read(self, path):
        cmd = self.api.joinPath(path.absolute, self.actions['GET'])
        try:
            data = self.api(cmd=cmd)
        except (TrapError, MultiTrapError) as error:
            raise ReadError(error)
        # Filter out rows which are dynamic.
        data = tuple(CmdPathRow(row) for row in data if not row.get('dynamic'))
        for row in data:
            logger.debug('{path} {action} {row}'.format(path=path.absolute, action='GET', row=row))
        return data

    def write(self, path, action, data):
        pass

    def close(self):
        self.api.close()


class RW_RouterOs(RO_RouterOs):
    '''
    Read, write RouterOs.
    '''

    def write(self, path, action, data):
        command = self.api.joinPath(path.absolute, self.actions[action])
        method = getattr(self, action)
        for row in data:
            try:
                logger.info('{path} {action} {row}'.format(path=path.absolute, action=action, row=row))
                method(command=command, data=row)
            except (TrapError, MultiTrapError) as error:
                raise WriteError(error)

    def DEL(self, command, data):
        self.api(cmd=command, **{'.id': data['.id']})

    def SET(self, command, data):
        self.api(cmd=command, **data)

    def ADD(self, command, data):
        self.api(cmd=command, **data)
