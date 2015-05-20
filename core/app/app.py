import subprocess as sp
import sys
import os.path as osp
from ..state import state

#filenames definitions
CMD_FILENAME        = "cmd"
NAME_FILENAME       = "name"
TIMES_FILENAME      = "times.rdt"
OPT_CONFIG_FILENAME = "pre_conf.sh"
LAST_LOG_FILENAME   = "last.log"
HIST_LOG_FILENAME   = "hist.log"
APP_CONFIGS_DIRNAME = "confs"
APP_RESUME_DIRNAME  = "resume"

def createStruct(path, files=[CMD_FILENAME,TIMES_FILENAME,LAST_LOG_FILENAME,HIST_LOG_FILENAME]):
    """ creates a struct for an app with necessary information for it to be run.
        path: a string designing the path of a dir where it will be saved"""
    commands = [ ["mkdir","-p",path] ] + [ ["touch",path + "/" + fl] for fl in files ]
    for cmd in commands:
        sp.Popen(cmd,stdout=sp.PIPE,stderr=sp.PIPE)

class App:
    """Represents information about an application. use either struct_dir to specify the app's directory or cmd to specify a string that invokes the command"""

    def __init__(self, struct_dir="", cmd=[], name="", priority=-1):
        """cmd is the command that runs the application, name is an alias for it. If struct_dir is specified, it will look inside this directory looking for a file named 'cmd' to use as cmd"""
        self.name = name
        self.cmd = cmd
    
        if struct_dir != "":
            #looking in specified dir to open cmd file
            f = open(struct_dir + "/" + CMD_FILENAME,"r")
            self.cmd = [ line.replace("\n","") for line in f ]
            f.close()
            if name == "" and osp.isfile(struct_dir + "/" + NAME_FILENAME):
                f = open(struct_dir + "/" + NAME_FILENAME,"r")
                self.name = f.read()
                f.close()

        #checking if there is an optional script to run
        if osp.isfile(struct_dir + "/" + OPT_CONFIG_FILENAME):
            sp.Popen([struct_dir + "/" + OPT_CONFIG_FILENAME]).wait() 
             
        self.struct_dir = struct_dir
        self.process    = None
        self.run_dir    = ""
        self.out        = ""
        self.err        = ""
        
    def createRunDir(self, base_dir="."):
        self.run_dir = base_dir + "/" + self.name
        for d in [APP_RESUME_DIRNAME,APP_CONFIGS_DIRNAME]:
            proc = sp.Popen(["mkdir","-p",self.run_dir + "/" + d])
            proc.wait()

    def run(self, args=[], out=sp.PIPE, err=sp.PIPE, source=None, cmdstate=False):
        """ runs command specified by cmd and stores outputs in pipes by default. args must be a list """
        cmd = self.cmd + args
        if cmdstate:
            cmd = sum( state.CmdState.get() + [cmd], [] )
        self.process = sp.Popen(cmd, stdout=out, stderr=err, stdin=source)
        self.out,self.err = self.process.communicate()
        return self.process.returncode

    def dump(self, out=sys.stdout, err=sys.stderr):
        """ dumps output of command into specified file """
        if out != None:
            out.write(self.out)
        if err != None:
            err.write(self.err) 
        out.close()
        err.close()

    def clear(self):
        self.out,self.err = "",""

class Extractor(App):
    """ Extracts some information from some application. To accomplish this, a filter script and an optional runner script are specifieds. It must comply with the following protocol: runner scripts may use the cmd of the app to be measured as argument and it's relevant output must be in stdout. filter script takes something from some file and must store relevant output in stdout."""
    def __init__(self, struct_dir="", filter_script="", name=""):
        App.__init__(self,struct_dir,filter_script,name)

    def createRunDir(self):
        pass

    def run():
        pass

    def extract(self, args=[], source=None, out=sp.PIPE, err=sp.PIPE):
        App.run(self,args,out,err,source)
