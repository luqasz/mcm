# -*- coding: UTF-8 -*-

'''
Module that holds configuration classes and helpers.
'''

from types import MethodType

from exc import ConfigRunError


class CmdPathConfigurator:


    def __init__(self, **kwargs):
        self.repository = kwargs['repository']
        self.master = kwargs['master']
        self.slave = kwargs['slave']
        self.ADD = MethodType( kwargs['addfunc'], self )
        self.DEL = MethodType( kwargs['delfunc'], self )
        self.SET = MethodType( kwargs['setfunc'], self )


    def run(self, path, modord):

        master_data = self.repository.read( device=self.master, path=path )
        slave_data = self.repository.read( device=self.slave, path=path )
        data = slave_data.compare(master_data)
        for action in modord:
            action_data = CmdPathConfigurator.extartActionData( data=data, elem=action )
            func = getattr(self, action)
            func(action_data)


    def extartActionData(data, elem):

        ADD, SET, DEL = data
        map = {'ADD':ADD, 'SET':SET, 'DEL':DEL}
        return map[elem]



def realADD(self, data, path):

    for row in data:
        self.repository.write(device=self.slave, data=(row,), path=path.add)


def realDEL(self, data, path):

    for row in data:
        self.repository.write(device=self.slave, data=(row,), path=path.remove)


def realSET(self, data, path):

    for row in data:
        self.repository.write(device=self.slave, data=(row,), path=path.set)


def dummyADD(self, data, path):

    for row in data:
        pass


def dummyDEL(self, data, path):

    for row in data:
        pass


def dummySET(self, data, path):

    for row in data:
        pass




def get_strategy(strategy):

    dry_run = {'addfunc':dummyADD, 'delfunc':dummyDEL, 'setfunc':dummySET}
    exact = {'addfunc':realADD, 'delfunc':realDEL, 'setfunc':realSET}
    ensure = {'addfunc':realADD, 'delfunc':dummyDEL, 'setfunc':realSET}
    map = {'dry_run':dry_run, 'ensure':ensure, 'exact':exact}

    return map[strategy]




class Configurator:
    pass
