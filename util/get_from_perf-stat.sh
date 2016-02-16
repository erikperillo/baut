#!/bin/bash

cpus_per_node=8

event=$1

if [[ $(echo $2 | head -c2) == "-n" ]]; then
    cpu_groups=true
    file=$3
else
    cpu_groups=false
    file=$2
fi

([[ -z $file ]] || [[ -z $event ]]) && { echo "error: must pass input file and event"; exit 1; }

case $event in
    "lsq_load")
        pattern="r510123" ;;
    "lsq_store")
        pattern="r510223" ;;
    "lsq_load_store")
        #pattern="r20000530323" ;;
        pattern="r530323" ;;
    "cycles")
        pattern=",cycles" ;;
    "stalled-cycles-backend")
        pattern="stalled-cycles-backend" ;;
    "instructions")
        pattern="instructions" ;;
    "mem_acc_local_to_"*)
        mask=$(printf "0x%x" $((1 << $(echo $event | rev | cut -f1 -d_ | rev))))
        pattern="amd_nb/event=0x1e0,umask=$mask/" ;;
    *)
        echo "warning: unknown event '$event', pattern will be the event string"
        pattern=$event
esac

if $cpu_groups; then
    col=2
    target=$(mktemp)
    node_num=$(echo $2 | tail -c +3)
    #assuming number of cores is 8 per node
    cpu_pattern="CPU"$((node_num*0))
    grep -A$cpus_per_node $cpu_pattern $file > $target
else
    col=2
    target=$file
fi

grep $pattern $target | cut -f$col -d, | paste -s -d+ | bc
