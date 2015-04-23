import core.benchmark as bm
import core.extractor as ext
import tools.oarg as oarg
import subprocess as sp

app = oarg.Oarg(str,"-a --app","","app to measure time",1)
help = oarg.Oarg(bool,"-h --help",False,"this help message")

oarg.parse()

if help.wasFound() or not app.wasFound():
     oarg.describeArgs("available options:")     
     exit()

timer = ext.Extractor("exts/time_filter.sh","exts/time_runner.sh")

timer.extract(app.getVal())
output = timer.filter()

print "output:",output
