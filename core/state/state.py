import subprocess as sp

class SysState(object):
    def __init__(self,getter=None,setter=None,typename=str,start_val=None):
        self.getter = getter
        self.setter = setter
        self.typename = typename
        self._val = start_val if getter == None else None

    @property
    def val(self,args=[]):
        if self.getter == None:
            return self._val
        if type(self.getter) == str:
            self.getter = self.getter.split()
        proc = sp.Popen(self.getter + args,stdout=sp.PIPE,stderr=sp.PIPE)
        self._val = proc.communicate()[0]
        return self.typename(self._val)

    @val.setter
    def val(self,value,args=[]):
        if self.setter != None:
            if type(self.setter) == str:
                self.setter = self.setter.split()
            proc = sp.Popen(self.setter + [str(value)] + args,stdout=sp.PIPE,stderr=sp.PIPE)
            proc.wait()
        else:
            self._val = value 

class RuntimeState(object):
    def __init__(self,key,activated=False,priority=-1):
        self.key = key
        self.activated = activated
        self.priority = priority
