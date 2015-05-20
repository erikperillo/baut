import subprocess as sp
import sys

#filenames definitions
KEY_FILENAME        = "key"
TIMES_FILENAME      = "times.rdt"
LAST_LOG_FILENAME   = "last.log"
HIST_LOG_FILENAME   = "hist.log"
APP_CONFIGS_DIRNAME = "confs"
APP_RESUME_DIRNAME  = "resume"

def createStruct(path, files=[KEY_FILENAME,TIMES_FILENAME,LAST_LOG_FILENAME,HIST_LOG_FILENAME]):
    """ creates a struct for an app with necessary information for it to be run.
        path: a string designing the path of a dir where it will be saved"""
    commands = [ ["mkdir","-p",path] ] + [ ["touch",path + "/" + fl] for fl in files ]
    for cmd in commands:
        sp.Popen(cmd,stdout=sp.PIPE,stderr=sp.PIPE)

class App:
    """Represents information about an application. use either struct_dir to specify the app's directory or key to specify a string that invokes the command"""

    def __init__(self, struct_dir="", key="", name=""):
        """key is the command that runs the application, name is an alias for it. If struct_dir is specified, it will look inside this directory looking for a file named 'key' to use as key"""
        self.key = "".join(open(struct_dir + "/" + KEY_FILENAME,"r").read().splitlines()) if struct_dir == "" else key
        self.name = [i for i in struct_dir.split("/") if i != ""][-1] if name == "" else name
        self.struct_dir = struct_dir
        self.process = None
        self.run_dir = ""
        self.out = ""
        self.err = ""
        
    def createRunDir(self, base_dir="."):
        self.run_dir = base_dir + "/" + self.name
        for d in [APP_RESUME_DIRNAME,APP_CONFIGS_DIRNAME]:
            proc = sp.Popen(["mkdir","-p",self.run_dir + "/" + d])
            proc.wait()

    def run(self,args=[], out=sp.PIPE, err=sp.PIPE):
        """ runs command specified by key and stores outputs in pipes by default. args must be a list """
        cmd = [self.key] + args
        self.process = sp.Popen(cmd,stdout=out,stderr=err)
        self.out,self.err = self.process.communicate()
        return self.process.returncode

    def dump(self, out=sys.stdout, err=sys.stderr):
        """ dumps output of command into specified file """
        if out != None:
            out.write(self.out)
        if err != None:
            err.write(self.err) 

class Extractor(App):
    """ Extracts some information from some application. To accomplish this, a filter script and an optional runner script are specifieds. It must comply with the following protocol: runner scripts may use the key of the app to be measured as argument and it's relevant output must be in stdout. filter script takes something from some file and must store relevant output in stdout."""
    def __init__(self, filter_script, struct_dir="", key="", name=""):
        App.__init__(self,struct_dir,key,name)
        self.filter_script = filter_script 
        self.filter_process = None

    def extract(self,source=None):
        if source == None:
            source = self.process.stdout
        self.process = sp.Popen(self.filter_script,stdin=source,stdout=sp.PIPE,stderr=sp.PIPE)
