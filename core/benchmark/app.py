import subprocess
import sys

class App:
     def __init__(self,key):
          self.key = key
          self.process = None

     def run(self,args=""):
          cmd = self.key + args
          self.process = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
          return self.process.wait()

     def dump(self,stdout=sys.stdout,stderr=sys.stderr):
          out, err = self.process.communicate()
          if stdout != None:
               stdout.write(out)
          if stderr != None:
               stderr.write(err)
