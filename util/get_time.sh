#!/bin/bash

#gets time from file.
#supposes it is in form 'elapsed_s,user_s,sys_s\n%e,%U,%S'

file=$2
event=$1

([[ -z $file ]] || [[ -z $event ]]) && { echo "error: must pass file and event"; exit 1; }

case $event in
    "elapsed"|"wall")
        col=1 ;;
    "user"|"usr")
        col=2 ;;
    "system"|"sys")
        col=3 ;;
    *)
        echo "error: invalid time event '$event'"
        exit 1 ;;
esac

cut -f$col -d, $file | tail -n1
