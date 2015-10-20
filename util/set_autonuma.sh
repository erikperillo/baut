#!/bin/bash

value=$1

[[ -z $value ]] && { echo "error: must specify input value"; exit 1; }

echo $value > /proc/sys/kernel/numa_balancing
