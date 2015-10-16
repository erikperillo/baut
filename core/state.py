import subprocess as sp

class SystemState(object):
    """this class represents some system state. 
       it can obtain/modify such state via 'val' property/setter. 
       those are an abstration of the use of the getter/setter scripts.
       getter: str / list of strings
       setter: str / list of strings"""
    def __init__(self, getter, setter):
        self.getter = getter.split() if isinstance(getter, str) else getter
        self.setter = setter.split() if isinstance(setter, str) else setter

    @property
    def val(self):
        """the getter must be something that puts its result into stdout. 
           it is returned as a string by default."""
        proc = sp.Popen(self.getter, stdout=sp.PIPE, stderr=sp.PIPE)
        return proc.communicate()[0]

    @val.setter
    def val(self, value):
        """the setter must be something (eg. shell script) that takes value as first argument.
           value: * (will be converted to string)"""
        proc = sp.Popen(self.setter + [value], stdout=sp.PIPE, stderr=sp.PIPE)
        proc.wait()
