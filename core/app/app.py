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
    """ abstraction of an application. use either struct_dir to specify the app's directory or key to specify a string that invokes the command"""
    def __init__(self, struct_dir=None, key="", name=""):
        if struct_dir == None:
            self.key = key
            self.name = name
        else:
            self.key = "".join(open(struct_dir + "/" + KEY_FILENAME,"r").read().splitlines())
            self.name = [i for i in struct_dir.split("/") if i != ""][-1]
        self.struct_dir = struct_dir
        self.process = None
        self.run_dir = None
        
    def createRunDir(self, base_dir="."):
        self.run_dir = base_dir + "/" + self.name
        for d in [APP_RESUME_DIRNAME,APP_CONFIGS_DIRNAME]:
            proc = sp.Popen(["mkdir","-p",self.run_dir + "/" + d])
            proc.wait()

    def run(self,args=[], out=sp.PIPE, err=sp.PIPE):
        """ runs command specified by key and stores outputs in pipes by default. args must be a list """
        cmd = [self.key] + args
        self.process = sp.Popen(cmd,stdout=out,stderr=err)
        return self.process.wait()

    def dump(self, stdout=sys.stdout, stderr=sys.stderr):
        """ dumps output of command into specified file """
        out,err = self.process.communicate()
        if stdout != None:
            stdout.write(out)
        if stderr != None:
            stderr.write(err) 

class Extractor(App):
    """ extracts some information from some application. to accomplish this, a filter script and an optional runner script are specifieds.
        it must comply with the following protocol: runner scripts may use the key of the app to be measured as argument and it's relevant output must be in stdout. filter script takes something from some file and must store relevant output in stdout."""
    def __init__(self, filter_script, struct_dir=None,  key=""):
        App.__init__(self,struct_dir,key)
        self.filter_script = filter_script 
        self.filter_process = None

    def filter(self,source=None):
        if source == None:
            source = self.process.stdout
        self.process = sp.Popen(self.filter_script,stdin=source,stdout=sp.PIPE,stderr=sp.PIPE)
