import core.app as app
import tools.oarg as oarg
import subprocess as sp

appl = app.App(key="ls")
print "ctor()"
appl.run()
print "run()"
#appl.dump()
#print "dump()"
ext = app.Extractor("exts/timer/time_filter.sh",key="exts/timer/time_runner.sh")
print "ext.ctor()"
ext.run([appl.key,"-l"])
print "ext.run()"
ext.filter()
print "ext.filter()"
ext.dump()
print "ext.dump()"
