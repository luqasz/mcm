# -*- coding: UTF-8 -*-

from types import MethodType



class CmdPathConfigurator:


    def __init__(self, configurator, path, addfunc, setfunc, delfunc):
        self.configurator = configurator
        self.path = path
        self.ADD = MethodType( addfunc, self )
        self.DEL = MethodType( delfunc, self )
        self.SET = MethodType( setfunc, self )


    def run(self):

        data = self.readData()
        result = self.compareData(data)
        self.applyData(data=result)


    def applyData(self, data):

        for action in self.path.modord:
            action_data = self.extartActionData( data=data, action=action )
            action_method = getattr(self, action)
            action_method(action, action_data)


    def compareData(self, data):

        master_data, slave_data = data
        result = slave_data.compare(master_data)
        return result


    def readData(self):

        master_data = self.configurator.master.read( path=self.path )
        slave_data = self.configurator.slave.read( path=self.path )
        return master_data, slave_data


    @staticmethod
    def extartActionData(data, action):

        ADD, SET, DEL = data
        action_map = {'ADD':ADD, 'SET':SET, 'DEL':DEL}
        return action_map[action]




def real_action(self, action, data):

    self.configurator.slave.write(data=data, path=self.path, action=action)


def no_action(self, action, data):
    pass



def getStrategyMethods(strategy):

    exact = real_action, real_action, real_action
    ensure = real_action, no_action, real_action
    strategy_map = {'ensure':ensure, 'exact':exact}

    return strategy_map[strategy]


def mkCmdPathConfigurator(configurator, path):
    addmethod, delmethod, setmethod = getStrategyMethods(strategy=path.strategy)
    return CmdPathConfigurator(path=path, configurator=configurator, addfunc=addmethod, setfunc=setmethod, delfunc=delmethod)




class Configurator:


    def __init__(self, master, slave):
        self.master = master
        self.slave = slave


    def run(self, paths):
        for path in paths:
            configurator = mkCmdPathConfigurator(configurator=self, path=path)
            configurator.run()

