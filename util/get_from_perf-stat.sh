#!/bin/bash

file=$1
event=$2

([[ -z $file ]] || [[ -z $event ]]) && { echo "error: must pass input file and event"; exit 1; }

case $event in
    "lsq_load")
        pattern="r510123" ;;
    "lsq_store")
        pattern="r510223" ;;
    "cycles")
        pattern=",cycles" ;;
    "stalled-cycles-backend")
        pattern="stalled-cycles-backend" ;;
    "instructions")
        pattern="instructions" ;;
    *)
        echo "warning: unknown event '$event', pattern will be the event string"
        pattern=$event
esac

if [[ ! -z $(cut -f1 -d, $file | grep "cpu\|CPU") ]]; then
    col=2
else
    col=1
fi

grep $pattern $file | cut -f$col -d, | paste -s -d+ | bc
