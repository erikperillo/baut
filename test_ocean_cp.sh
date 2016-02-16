#!/bin/bash

info()
{
   echo "[test_ocean_cp.sh] $1" 
}

error()
{
    info "$1"
    exit 1
}

parsec_dir=/local/erik/parsec_custom/parsec-3.0

#needed libraried
export LD_PRELOAD=$LD_PRELOAD:/local/ufmg/henrique/root/lib/libginac.so.2.1.0
export LD_PRELOAD=$LD_PRELOAD:/local/ufmg/henrique/root/lib/libcln.so.6

for t in default; do # lock nolock; do
    info "in $t"

    #info "building... "
    #(cd /local/erik/parsec_custom/parsec-3.0/ && ./build_ocean_cp.sh $t) || error "failed building"

    info "running ..."
    /local/erik/baut/baut.py run -s /local/erik/baut/states/states.csv -d /local/erik/baut/runs/ocean_cp_$t
done
