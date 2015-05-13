import state

numa_balancing = state.SysState("numa balancing",getter=["head","-c","1","/proc/sys/kernel/numa_balancing"],setter=["python","../../tools/numa/numa_bal_config.py","-a"])

print "numa balancing is",numa_balancing.val
numa_balancing.val = not numa_balancing.val[0] in ["1","True","true"]
print "numa balancing is",numa_balancing.val
