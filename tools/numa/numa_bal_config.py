#!/usr/bin/python
#sets automatic numa balancing parameters

import sys
sys.path.append("../oarg")
import oarg

NUMA_BALANCING_COMMON="/proc/sys/kernel/numa_balancing"

#numa balancing parameters
numa_balancing  = oarg.Oarg(bool,"-a --activated",False,"Sets automatic NUMA balancing on/off")
scan_delay      = oarg.Oarg(int,"--sd --scan-delay",1000,"Scan delay in milliseconds")
scan_size       = oarg.Oarg(int,"--ss --scan-size",256,"Scan size in megabytes")
scan_period_min = oarg.Oarg(int,"--spmin --scan-period-min",1000,"Minimum scan period in millisseconds")
scan_period_max = oarg.Oarg(int,"--spmax --scan-period-max",6000,"Maximum scan period in millisseconds")
migrate_def 	= oarg.Oarg(int,"--md --migrate-deferred",16,"Migrate deferred parameter")
settle_count 	= oarg.Oarg(int,"--sc --settle-count",4,"Settle count parameter")
default		= oarg.Oarg(bool,"-d --default",False,"Set all parameters to default")
hlp             = oarg.Oarg(bool,"-h --help",False,"This help message")

#checking args validity
if oarg.parse() != 0:
    print "error: invalid arguments:"
    print oarg.Oarg.invalid_options
    exit()

if hlp.getVal():
    print "Avaliable options:"
    oarg.describeArgs()
    exit()

#determining parameters to change
params = {"": numa_balancing, "_scan_delay_ms": scan_delay, "_scan_size_mb": scan_size, "_scan_period_min_ms": scan_period_min, "_scan_period_max_ms": scan_period_max, "_migrate_deferred": migrate_def, "_settle_count": settle_count}
to_change = params if default.getVal() else dict([ (key,val) for key,val in params.iteritems() if val.wasFound()])

#setting
for key,val in to_change.iteritems():
    fd = open(NUMA_BALANCING_COMMON + key,"w")
    fd.write(str(int(val.getVal())))
    fd.close()
