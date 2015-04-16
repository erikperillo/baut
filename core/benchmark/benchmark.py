import os

class Benchmark:
     def __init__(self,apps,run_cmd,cfg_script=None):
          self.apps = dict((app.name,app) for app in apps)
          self.run_cmd_prekey = run_cmd[0]
          self.run_cmd_poskey = run_cmd[1]

          if cfg_script != None:
               os.system(cfg_script)       

     def run(self,app_name,opt_args=""):
          cmd = self.run_cmd_prekey + self.apps[app_name].key + self.run_cmd_poskey + opt_args 
          print "running command '" + cmd + "' ..." 
          os.system(cmd)
