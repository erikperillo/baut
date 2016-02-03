#!/bin/bash

value=$1

echo "oi"
[[ -z $value ]] && { echo "error: must specify input value"; exit 1; }

echo "set_autonuma called with value = $value"
echo "previous value: $(cat /proc/sys/kernel/numa_balancing)"
echo $value > /proc/sys/kernel/numa_balancing || { echo "error setting autonuma"; exit 1; }
echo "done. new value: $(cat /proc/sys/kernel/numa_balancing)"
