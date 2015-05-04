import subprocess as sp
import exceptions

class Extractor:
     def __init__(self, filter_script, run_script=None):
          self.filter_script = filter_script
          self.run_script = run_script
          self.source = None

     def extract(self, key):
          self.source = sp.Popen([self.run_script,key], stdout=sp.PIPE, stderr=sp.PIPE) 

     def filter(self, source=None):
          if source == None:
               source = self.source
          process = sp.Popen(self.filter_script, stdin=source.stdout, stdout=sp.PIPE, stderr=sp.PIPE) 
          stdout,stderr = process.communicate()
          if stderr != "":
               raise exceptions.ExtractingError("stderr is not empty")
          return stdout 
