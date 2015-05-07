#!/usr/bin/python
#sets automatic numa balancing parameters

import sys
import oarg

NUMA_BALANCING_COMMON="/proc/sys/kernel/numa_balancing"

#numa balancing parameters
numa_balancing  = oarg.Oarg(bool,"-a --activated",False,"Sets automatic NUMA balancing on/off")
scan_delay      = oarg.Oarg(int,"-d --scan-delay",1000,"Scan delay in milliseconds")
scan_size       = oarg.Oarg(int,"-s --scan-size",256,"Scan size in megabytes")
scan_period_min = oarg.Oarg(int,"-m --scan-period-min",1000,"Minimum scan period in millisseconds")
scan_period_max = oarg.Oarg(int,"-M --scan-period-max",6000,"Maximum scan period in millisseconds")
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

params = ["","_scan_delay_ms","_scan_size_mb","_scan_period_min_ms","_scan_period_max_ms"]
values = [numa_balancing,scan_delay,scan_size,scan_period_min,scan_period_max]

#setting
for param,value in zip(params,values):
    fd = open(NUMA_BALANCING_COMMON + param,"w")
    fd.write(str(int(value.getVal())))
    fd.close()
