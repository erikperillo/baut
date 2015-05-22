import subprocess as sp

#State class interface
class State(object):
    @property
    def val(self,args=[]):
        raise NotImplementedError("Need to implement part of this interface")
    
    @val.setter
    def val(self,value,args=[]):
        raise NotImplementedError("Need to implement part of this interface")

class SysState(State):
    """This class represents some system state. It can obtain/modify such state via 'val' property/setter. Those are an abstration of the use of the get/set scripts, specified by the attributes getter and setter.""" 
    def __init__(self, getter=None, setter=None, typename=str, start_val=None):
        self.getter = getter
        self.setter = setter
        self.typename = typename
        self._val = start_val if getter == None else None

    @property
    def val(self,args=[]):
        """The getter must be something that puts its result into stdout. It is returned as a string by default."""
        if self.getter == None:
            return self._val
        if type(self.getter) == str:
            self.getter = self.getter.split()
        proc = sp.Popen(self.getter + args,stdout=sp.PIPE,stderr=sp.PIPE)
        self._val = proc.communicate()[0]
        return self.typename(self._val)

    @val.setter
    def val(self,value,args=[]):
        """The setter must be something (eg. shell script) that takes value as first argument"""
        if self.setter != None:
            if type(self.setter) == str:
                self.setter = self.setter.split()
            proc = sp.Popen(self.setter + [str(value)] + args,stdout=sp.PIPE,stderr=sp.PIPE)
            proc.wait()
        else:
            self._val = value 

class CmdState(State):
    """This class represents the command line that will be used to run a program. Some stuff change programs' performance and are determined in the command line, so this is reasonable."""
    DESCRS = {}

    def __init__(self, cmd, priority=1, active=False):
        """cmd is the list of strings that'll go to the command, priotiry is the position os the command. The lower the number, the more it will be in the front (from left to right). Activate/deactivate it with 'val' setter."""
        key = " ".join(cmd)
        if key in CmdState.DESCRS:
            raise ValueError("duplicate key '" + key + "'")

        CmdState.DESCRS.update({key: [cmd,active,priority]})
        self.key = key 
        self.active = active

    @property
    def val(self):
        return self._active

    @val.setter
    def val(self,value):
        if type(value) != bool:
            raise ValueError("rvalue must be of type bool")

        self._active = value
        CmdState.DESCRS[self.key][1] = value 

    @staticmethod
    def get():
        """returns the whole command line as a list of strings."""
        ret = [(cmd,p) for _,(cmd,active,p) in CmdState.DESCRS.iteritems() if active]
        ret.sort(key=lambda x: x[-1])
        return [i for i,_ in ret]
        
    @staticmethod
    def clear():
        """clears the line."""
        CmdState.DESCRS = {}
