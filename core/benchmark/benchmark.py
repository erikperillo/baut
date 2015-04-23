import subprocess

class Benchmark:
     def __init__(self,apps_keys,run_cmd,sys_cfg_script=None):
          self.apps_keys = apps_keys
          self.run_cmd_prekey = run_cmd[0]
          self.run_cmd_poskey = run_cmd[1]

          if sys_cfg_script != None:
               os.system(cfg_script)       

     def run(self,app_key,opt_args=""):
          cmd = self.run_cmd_prekey + app_key + self.run_cmd_poskey + opt_args 
          print "simulating system running command '" + cmd + "' ..." 
          #os.system(cmd)
