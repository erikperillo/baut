import sys
import re

class Oarg:
    invalid_options = []
    def __init__(self, tp, names, def_val, description, pos_n_found=-1):
        self.tp           = tp
        self.names        = [Oarg.pureName(n) for n in (names.split() if type(names) == str else names)]
        self.def_val      = def_val
        self.description  = description
        self.pos_n_found  = pos_n_found
        self.found        = False
        self.str_vals     = []
        self.vals         = (def_val,)
        Container.add(self)

    @property
    def val(self):
        return self.vals[0]    

    def setVals(self,str_vals,falses):
        self.str_vals = str_vals
        self.found = True
        if self.tp == bool:
            self.vals = tuple( not i.lower() in falses for i in self.str_vals ) if self.str_vals != [] else (not self.def_val,)
        else:
            self.vals = tuple( self.tp(i) for i in self.str_vals ) if self.str_vals != [] else (self.def_val,)
        
    @staticmethod
    def pureName(name):
        while name[0] == "-":
            name = name[1:]
        return name

    @staticmethod
    def clName(name):
        insertion = "-"
        return insertion + name

    @staticmethod
    def isClName(name):
        return (name[0] == "-" and (ord(name[1]) < 48 or ord(name[1]) > 57)) if len(name) > 1 else False
        
class Container:
    oargs = []
    @staticmethod
    def add(oarg):
        Container.oargs.append(oarg)

def parse(source=sys.argv,falses=["false","no","n","0"]):
    _src = list(source)[1:] #assuming first argument is program's name
    
    for i,elem in enumerate(_src):
        _elem = re.sub(r'(?<!\\),',',,',elem)
        _src[i] = re.sub(r'\\,',',',_elem)

    src = ",".join(_src)
    while src.find(",,,") >= 0:
        src = src.replace(",,,",",,")

    src = re.split(r'[ ,]-(?![0-9])'," " + src)
    src[0] = src[0][1:]

    oargs_dict = dict( (Oarg.pureName(key),val) for val in Container.oargs for key in val.names )

    remaining = []
    for __cand in src:
        _cand = __cand.split(",,")
        cand = _cand[0]
        remaining_partial = _cand[1:]
        cands = cand.split(",")

        if ("-" + cands[0]) in sys.argv:
            opt = cands[0]
            args = cands[1:]
            #print "\topt:",opt
            #print "\targs:",args
            if opt in oargs_dict:
                oarg = oargs_dict[opt]
                oarg.setVals(args,falses)
            else:
                Oarg.invalid_options.append(opt)
        else:
            remaining_partial = [_cand[0]] + remaining_partial

        remaining += remaining_partial

    remaining = [ i for i in remaining if i != "" ]

    left_oargs = [ o for o in Container.oargs if not o.found and o.pos_n_found >= 0 ]
    if left_oargs != []: 
        left_oargs.sort(key=lambda x: x.pos_n_found)

    while len(remaining) > 0 and len(left_oargs) > 0:
        oarg = left_oargs[0]    
        oarg.setVals(remaining[0].split(","),falses)
        remaining = remaining[1:]
        left_oargs = left_oargs[1:]

    return len(Oarg.invalid_options)


def describeArgs(helpmsg=""):
    if helpmsg != "":
        print helpmsg
    for oarg in Container.oargs:
        names = ""
        for i in range(len(oarg.names)-1):
            names += Oarg.clName(oarg.names[i]) + ", "
        names += Oarg.clName(oarg.names[len(oarg.names)-1])
        print "{0:48}{1}".format(names,oarg.description)
