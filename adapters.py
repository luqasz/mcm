# -*- coding: UTF-8 -*-

from datastructures import CmdPathRow
from exceptions import WriteError

from logging import getLogger


logger = getLogger('mcm.' + __name__)


class MasterAdapter:


    def __init__(self, device):
        self.device = device


    def read(self, path):
        content = self.device.read(path=path.absolute)
        data = self.assemble_data(data=content)
        for row in data:
            logger.debug('{path} {data}'.format(path=path.absolute, data=row))
        return data


    def close(self):
        self.device.close()


    @staticmethod
    def assemble_data(data):
        return tuple(CmdPathRow(data=elem) for elem in data)



class SlaveAdapter(MasterAdapter):


    def write(self, path, action, data):
        for row in data:
            try:
                self.device.write(path=path.absolute, action=action, data=row.data)
                logger.info('{path} {action} {data}'.format(path=path.absolute, action=action, data=row))
            except WriteError as error:
                logger.error('Failed to send {path} {action} {data} to device: {reason}'.format(path=path.absolute, action=action, data=row, reason=error))

