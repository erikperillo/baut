import subprocess as sp
import shlex

class SystemState(object):
    """this class represents some system state. 
       it can obtain/modify such state via 'val' property/setter. 
       those are an abstration of the use of the getter/setter scripts.
       getter: str / list of strings
       setter: str / list of strings"""
    def __init__(self, getter, setter):
        self.getter = shlex.split(getter) if isinstance(getter, str) else getter
        self.setter = shlex.split(setter) if isinstance(setter, str) else setter

    def __getitem__(self, key):
        """calls getter when arguments are provided.  it is returned as a string by default.
           key must be a string"""
        args = shlex.split(key)
        proc = sp.Popen(self.getter + args, stdout=sp.PIPE, stderr=sp.PIPE)
        return proc.communicate()[0]


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
        print "lol"
        proc = sp.Popen(self.setter + [str(value)], stdout=sp.PIPE, stderr=sp.PIPE)
        #proc.wait()
        out, err = proc.communicate()
        print "out: %s" % out
        print "err: %s" % err
        print "flw"
        proc = sp.Popen(self.setter + [str(value)], stdout=sp.PIPE, stderr=sp.PIPE)
