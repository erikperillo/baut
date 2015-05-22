import sys

class Oarg:
     invalid_options = []
     def __init__(self, tp, names, def_val, description, pos_n_found=0):
          self.tp             = tp
          self.names          = list(names.split())
          self.def_val        = def_val
          self.description    = description
          self.pos_n_found    = pos_n_found
          self.found          = False
          self.str_vals       = []
          self.vals           = None
          for i in range(len(self.names)):
               self.names[i] = Oarg.pureName(self.names[i])
          Container.add(self)

     def getVal(self,index=0):
          if index >= 0 and index < len(self.str_vals):
               return self.vals[index]
          if self.tp is bool and self.found:
               return not self.def_val
          return self.def_val

     def getTupleVal(self):
          return self.vals

     def wasFound(self):
          return self.found

     def setTuple(self):
          if len(self.str_vals) == 0:
               if self.tp == bool and self.found:
                    self.vals = (not self.def_val,)
               else:
                    self.vals = (self.def_val,)
               return
          if self.tp == bool:
               self.vals = tuple( i in ["True","true","TRUE","y","yes","Y","Yes","YES","1"] for i in self.str_vals )
          else:
               self.vals = tuple(self.tp(i) for i in self.str_vals)
          
     @staticmethod
     def pureName(name):
          while name[0] == "-":
               name = name[1:]
          while name[len(name)-1] == ":":
               name = name[:(len(name)-1)]
          return name

     @staticmethod
     def clName(name):
          insertion = "-"
          if len(name) > 1:
               insertion += "-"
          return insertion + name

     @staticmethod
     def isClName(name):
          if len(name) < 2:
               return name[0] == "-"
          return name[0] == "-" and (ord(name[1]) < 48 or ord(name[1]) > 57) 
          
class Container:
     oargs = []
     @staticmethod
     def add(oarg):
          Container.oargs.append(oarg)

def osplit(string,delim=","):
     ret = []
     i = 0
     while i < len(string):
          if string[i] == delim:
               if i > 0 and string[i-1] == "\\":
                    string = string[:(i-1)] + string[i:]
                    i -= 1
               else:
                    if string[:i] != "":
                         ret.append(string[:i])
                    string = string[(i+1):]
                    i = -1
          i += 1
     if string != "":
          ret.append(string)
     return ret

def parse(argv=sys.argv):
     #list for oargs with pos_n_found
     pos_vec = []
     #main loop
     for oarg in Container.oargs:
          mark = None
          deleted = False
          for i,arg in enumerate(argv):
               if not oarg.found:
                    for name in oarg.names:
                         if arg == Oarg.clName(name):
                              oarg.found = True
                              mark = arg
                              break
               else:
                    if not deleted:
                         if not (oarg.tp == bool and Oarg.isClName(arg)):
                             oarg.str_vals = osplit(arg)
                             argv.remove(arg)
                         argv.remove(argv[i-1])
                         deleted = True
                         break
                    else:
                         continue
          if oarg.found and not deleted:
               argv.remove(mark)
               deleted = True
          #appendind to list of pos_n_found if set
          if not oarg.found and oarg.pos_n_found > 0:
               pos_vec.append(oarg)
          #setting tuple of values
          oarg.setTuple()
     #sorting in ascending order
     #checking validity of arguments
     for arg in argv:
          if(Oarg.isClName(arg)):
               Oarg.invalid_options.append(arg)
     pos_vec.sort(key=lambda x: x.pos_n_found)               
     #getting not read values from cl
     for oarg in pos_vec:
          if len(argv) > 1 and not Oarg.isClName(argv[1]): 
               oarg.str_vals = osplit(argv[1])
               oarg.found = True
               argv.remove(argv[1])
               oarg.setTuple()
     #returns number of unknown parameters
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
          #print names,"\t\t\t\t",oarg.description
