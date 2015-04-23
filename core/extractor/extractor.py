import subprocess
import exceptions

class Extractor:
     def __init__(self, filter_script, run_script=None):
          self.filter_script = filter_script
          self.run_script = run_script
          self.source = None

     def extract(self, key):
          self.source = subprocess.Popen([self.run_script,key], stdout=subprocess.PIPE, stderr=subprocess.PIPE) 

     def filter(self, source=None):
          if source == None:
               source = self.source
          process = subprocess.Popen(self.filter_script, stdin=source.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
          stdout,stderr = process.communicate()
          if stderr != "":
               raise exceptions.FilteringException("stderr is not empty") 
          return stdout 
