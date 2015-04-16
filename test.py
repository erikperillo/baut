import core.benchmark as bm
import tools.oarg as oarg

apps = oarg.Oarg(str,"-a --apps","","apps list",1)
help = oarg.Oarg(bool,"-h --help",False,"this help message")

oarg.parse()

if help.wasFound() or not apps.wasFound():
     oarg.describeArgs("available options:")     
     exit()

NPB = bm.Benchmark([bm.App(name) for name in apps.getTupleVal()],["echo '"," - HUE '"])

for app_name in apps.getTupleVal():
     NPB.run(app_name)
