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
    def __init__(self, getter=None, setter=None, typename=str, start_val=None):
        self.getter = getter
        self.setter = setter
        self.typename = typename
        self._val = start_val if getter == None else None

    """the getter must be something that puts it's result into stdout"""
    @property
    def val(self,args=[]):
        if self.getter == None:
            return self._val
        if type(self.getter) == str:
            self.getter = self.getter.split()
        proc = sp.Popen(self.getter + args,stdout=sp.PIPE,stderr=sp.PIPE)
        self._val = proc.communicate()[0]
        return self.typename(self._val)

    """the setter must be something that takes value as first argument"""
    @val.setter
    def val(self,value,args=[]):
        if self.setter != None:
            if type(self.setter) == str:
                self.setter = self.setter.split()
            proc = sp.Popen(self.setter + [str(value)] + args,stdout=sp.PIPE,stderr=sp.PIPE)
            proc.wait()
        else:
            self._val = value 

class CmdState(State):
    DESCRS = {}

    def __init__(self, key, active=False, priority=1):
        if key in CmdState.DESCRS:
            raise ValueError("duplicate key '" + key + "'")

        CmdState.DESCRS.update({key: [active,priority]})
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
        CmdState.DESCRS[self.key][0] = value 

    @staticmethod
    def get():
        ret = [(key,p) for key,(active,p) in CmdState.DESCRS.iteritems() if active]
        ret.sort(key=lambda x: x[1])
        return [i for i,_ in ret]
        
    @staticmethod
    def clear():
        CmdState.DESCRS = {}
