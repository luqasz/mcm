# -*- coding: UTF-8 -*-

'''
Module that holds configuration classes and helpers.
'''

from types import MethodType



class CmdPathConfigurator:


    def __init__(self, **kwargs):
        self.repository = kwargs['repository']
        self.master = kwargs['master']
        self.slave = kwargs['slave']
        self.ADD = MethodType( kwargs['addfunc'], self )
        self.DEL = MethodType( kwargs['delfunc'], self )
        self.SET = MethodType( kwargs['setfunc'], self )


    def run(self, path, modord):

        data = self.readData(path)
        result = self.compareData(data)
        self.applyData(path=path, data=result, modord=modord)


    def applyData(self, path, data, modord):

        for action in modord:
            action_data = CmdPathConfigurator.extartActionData( data=data, action=action )
            action_method = getattr(self, action)
            action_method(action_data, path)


    def compareData(self, data):

        master_data, slave_data = data
        result = slave_data.compare(master_data)
        return result


    def readData(self, path):

        master_data = self.readMaster(path)
        slave_data = self.readSlave(path)
        return master_data, slave_data


    def readMaster(self, path):

        path.cmd = path.getall
        return self.repository.read( device=self.master, path=path )


    def readSlave(self, path):

        path.cmd = path.getall
        return self.repository.read( device=self.slave, path=path )


    def extartActionData(data, action):

        ADD, SET, DEL = data
        action_map = {'ADD':ADD, 'SET':SET, 'DEL':DEL}
        return action_map[action]



def realADD(self, data, path):

    path.cmd = path.add
    for row in data:
        self.repository.write(device=self.slave, data=(row,), path=path)


def realDEL(self, data, path):

    path.cmd = path.remove
    for row in data:
        self.repository.write(device=self.slave, data=(row,), path=path)


def realSET(self, data, path):

    path.cmd = path.set
    for row in data:
        self.repository.write(device=self.slave, data=(row,), path=path)


def dummyADD(self, data, path):

    for row in data:
        pass


def dummyDEL(self, data, path):

    for row in data:
        pass


def dummySET(self, data, path):

    for row in data:
        pass




def getStrategyMethods(strategy):

    dry_run = {'addfunc':dummyADD, 'delfunc':dummyDEL, 'setfunc':dummySET}
    exact = {'addfunc':realADD, 'delfunc':realDEL, 'setfunc':realSET}
    ensure = {'addfunc':realADD, 'delfunc':dummyDEL, 'setfunc':realSET}
    strategy_map = {'dry_run':dry_run, 'ensure':ensure, 'exact':exact}

    return strategy_map[strategy]




class Configurator:
    pass
