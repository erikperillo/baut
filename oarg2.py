"""
Copyright (c) 2015, Erik Perillo
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import sys
import re

class UnknownOptionsError(Exception):
    def __init__(self,message,opts):
        Exception.__init__(self,message)
        self.opts = opts 

class RepeatedKeyError(Exception):
    def __init__(self,message,key):
        Exception.__init__(self,message)
        self.key = key 

class Oarg:
    oargs = []

    def __init__(self, tp, names, def_val, description, pos_n_found=-1):
        self.tp           = tp
        self.names        = [Oarg.pureName(n) for n in (names.split() if type(names) == str else names)]
        self.def_val      = def_val
        self.description  = description
        self.pos_n_found  = pos_n_found
        self.found        = False
        self.str_vals     = []
        self.vals         = (def_val,)

        for name in self.names:
            for oarg in Oarg.oargs:
                if name in oarg.names:
                    raise RepeatedKeyError("Key '" + Oarg.clName(name) + "' already exists",Oarg.clName(name))

        Oarg.oargs.append(self)

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

def parse(source=sys.argv,falses=["false","no","n","0"]):
    invalid_options = []

    _src = list(source)[1:] #assuming first argument is program's name
    for i,elem in enumerate(_src):
        _elem = re.sub(r'(?<!\\),',',,',elem)
        _src[i] = re.sub(r'\\,',',',_elem)

    src = ",".join(_src)
    while src.find(",,,") >= 0:
        src = src.replace(",,,",",,")

    src = re.split(r'[ ,]-(?![0-9])'," " + src)
    src[0] = src[0][1:]

    oargs_dict = dict( (Oarg.pureName(key),val) for val in Oarg.oargs for key in val.names )

    remaining = []
    for __cand in src:
        _cand = __cand.split(",,")
        cand = _cand[0]
        remaining_partial = _cand[1:]
        cands = cand.split(",")

        if ("-" + cands[0]) in sys.argv:
            opt = cands[0]
            args = cands[1:]
            if opt in oargs_dict:
                oarg = oargs_dict[opt]
                oarg.setVals(args,falses)
            else:
                invalid_options.append(Oarg.clName(opt))
        else:
            remaining_partial = [_cand[0]] + remaining_partial

        remaining += remaining_partial

    remaining = [ i for i in remaining if i != "" ]

    left_oargs = [ o for o in Oarg.oargs if not o.found and o.pos_n_found >= 0 ]
    if left_oargs != []: 
        left_oargs.sort(key=lambda x: x.pos_n_found)

    while len(remaining) > 0 and len(left_oargs) > 0:
        oarg = left_oargs[0]    
        oarg.setVals(remaining[0].split(","),falses)
        remaining = remaining[1:]
        left_oargs = left_oargs[1:]

    if len(invalid_options) > 0:
        raise UnknownOptionsError("Invalid options passed: " + ",".join(invalid_options),invalid_options)

def describeArgs(helpmsg="",width=48):
    if helpmsg != "":
        print helpmsg
    for oarg in Oarg.oargs:
        names = ",".join([ Oarg.clName(n) for n in oarg.names ])
        print ("{0:" + str(width) + "}{1}").format(names,oarg.description)
