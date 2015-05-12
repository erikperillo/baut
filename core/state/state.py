import subprocess as sp

class SysState(object):
    def __init__(self,name,start_val=None,getter=None,setter=None):
        self.name = name
        self.getter = getter
        self.setter = setter
        self.val = start_val 

    @property
    def val(self,args=[]):
        if self.getter == None:
            return self._val
        proc = sp.Popen([getter] + args,stdout=sp.PIPE,stderr=sp.PIPE)
        self._val = proc.communicate()[0]
        return self._val

    @val.setter
    def val(self,value,args=[]):
        if self.setter != None:
            proc = sp.Popen([self.setter] + [value] + args,stdout=sp.PIPE,stderr=sp.PIPE)
            proc.wait()
        else:
            self._val = value 

class RuntimeState(object):
    def __init__(self,name,key,activated=False,priority=-1):
        self.name = name
        self.key = key
        self.activated = activated
        self.priority = priority
