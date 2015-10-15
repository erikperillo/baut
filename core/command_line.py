import shlex
import subprocess as sp

class CommandLine(object):
    def __init__(self, command, before=[], after=[]):
        self.before = before
        self.command = command
        self.after = after

    def __str__(self):
        return " ".join(self.before + self.command + self.after)

    @property
    def before(self):
        return self._before

    @property
    def command(self):
        return self._command

    @property
    def after(self):
        return self._after

    @before.setter
    def before(self, value):
        self._before = shlex.split(value) if isinstance(value, str) else value 

    @command.setter
    def command(self, value):
        self._command = shlex.split(value) if isinstance(value, str) else value 

    @after.setter
    def after(self, value):
        self._after = shlex.split(value) if isinstance(value, str) else value 

    def run(self):
        process = sp.Popen(self.before + self.command + self.after, stderr=sp.PIPE, stdout=sp.PIPE) 
        return process.communicate()
