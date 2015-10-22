#!/bin/bash
run_dir=$1

#running
echo "[baut.sh] running ..."
./baut.py run -s states/states.csv -d $run_dir

#extracting
echo "[baut.sh] extracting ..."
for d in $run_dir/*/state_*; do
    ./baut.py extract -d $d -n cycles time_elapsed instructions lsq_load lsq_store
done

#resuming
echo "[baut.sh] resuming ..."
./util/resume.sh $run_dir/*
