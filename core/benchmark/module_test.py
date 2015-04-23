import subprocess as sp
import sys

if len(sys.argv) < 1+2:
     exit()

if sys.argv[2] == "file":
     source = sp.Popen(["cat",sys.argv[1]], stdout=sp.PIPE)
else:
     source = sp.Popen(sys.argv[1], stdout=sp.PIPE, shell=True)

ftr = sp.Popen("./time_filter.sh",stdin=source.stdout,stdout=sp.PIPE)

print ftr.communicate()
