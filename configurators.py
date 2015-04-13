# -*- coding: UTF-8 -*-

from types import MethodType

from comparators import get_comparator



class CmdPathConfigurator:


    def __init__(self, configurator, path, comparator, addfunc, setfunc, delfunc):
        self.configurator = configurator
        self.path = path
        self.comparator = comparator
        self.ADD = MethodType( addfunc, self )
        self.DEL = MethodType( delfunc, self )
        self.SET = MethodType( setfunc, self )


    @classmethod
    def with_ensure(cls, configurator, path):
        comparator = get_comparator(path=path)
        return cls(configurator=configurator, path=path, comparator=comparator,
                addfunc=real_action, setfunc=real_action, delfunc=no_action)

    @classmethod
    def with_exact(cls, configurator, path):
        comparator = get_comparator(path=path)
        return cls(configurator=configurator, path=path, comparator=comparator,
                addfunc=real_action, setfunc=real_action, delfunc=real_action)


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
        return self.comparator.compare(wanted=master_data, present=slave_data)


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






class Configurator:


    def __init__(self, master, slave):
        self.master = master
        self.slave = slave


    def run(self, paths):
        for path in paths:
            configurator = self.getPathConfigurator(path=path)
            configurator.run()


    def getPathConfigurator(self, path):
        strategy = 'with_' + path.strategy
        constructor = getattr(CmdPathConfigurator, strategy)
        return constructor(configurator=self, path=path)
