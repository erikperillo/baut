import subprocess as sp

types_dict = {"int": lambda x: int(x, 0),
              "float": float,
              "str": str}

class TypeNotSupported(Exception):
    """exception thrown when an invalid type is provided"""
    pass

class SystemState(object):
    """this class represents some system state. 
       it can obtain/modify such state via 'val' property/setter. 
       those are an abstration of the use of the getter/setter scripts.
       getter: str / list of strings
       setter: str / list of strings
       type_name: str""" 
    def __init__(self, getter, setter, type_name="str"):
        self.getter = getter.split() if isinstance(getter, str) else getter
        self.setter = setter.split() if isinstance(setter, str) else setter
        self.type_name = type_name

    @property
    def val(self):
        """the getter must be something that puts its result into stdout. 
           it is returned as a string by default."""
        proc = sp.Popen(self.getter, stdout=sp.PIPE, stderr=sp.PIPE)
        _val = proc.communicate()[0]
        try:
            return types_dict[self.type_name](_val)
        except KeyError:
            raise TypeNotSupported("type '%s' not supported. available ones: %s" % \
                                   (self.type_name, ", ".join(types_dict)))

    @val.setter
    def val(self, value):
        """the setter must be something (eg. shell script) that takes value as first argument.
           value: * (will be converted to string)"""
        print self.setter + [str(value)]
        proc = sp.Popen(self.setter + [str(value)], stdout=sp.PIPE, stderr=sp.PIPE)
        proc.wait()
