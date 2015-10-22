#!/bin/bash
run_dir=$1
measures="time_elapsed instructions cycles stalled-cycles-backend lsq_load lsq_store"

#running
echo "[baut.sh] running ..."
./baut.py run -s states/states.csv -d $run_dir

#selecting most recent dir
dir=$run_dir/$(ls -t $run_dir | head -n 1)

#extracting
echo "[baut.sh] extracting ..."
for d in $dir/state_*; do
    ./baut.py extract -d $d -n $measures
done

#resuming
echo "[baut.sh] resuming ..."
./util/resume.sh $dir $measures
