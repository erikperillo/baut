#!/bin/bash

perf_stat_out=$1
pattern=$2

([[ -z $perf_stat_out ]] || [[ -z $pattern ]]) && { echo "error: must pass input file and pattern"; exit 1; }

grep $pattern $perf_stat_out | cut -f2 -d,
