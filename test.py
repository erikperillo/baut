import core.app as app
import tools.oarg as oarg
import subprocess as sp

perf = app.App(key="perf")

apps = [ app.App(key=k) for k in ["ls","sleep 1","dmesg"] ]

for appl in apps:
    perf.run(["stat",appl.key])
    print "dumping..."
    perf.dump()
