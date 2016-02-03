#!/bin/bash

get_mem_acc_events()
{
    local measures=""
    for i in $(seq 0 7); do
        for j in $(seq 0 7); do
            measures+="mem_acc_"$i"_to_"$j" "
        done
    done    
    echo $measures
}

run_dir=$1
states_file=$2
measures="time_elapsed instructions "$(get_mem_acc_events)
#measures="lsq_load_store_node_0 lsq_load_store_node_1 lsq_load_store_node_2 lsq_load_store_node_3 lsq_load_store_node_4 lsq_load_store_node_5 lsq_load_store_node_6 lsq_load_store_node_7"
#measures=$(get_mem_acc_events)

#running
echo "[run_extract_resume.sh] running ..."
./baut.py run -s states/$states_file -d $run_dir 

#selecting most recent dir
dir=$run_dir/$(ls -t $run_dir | head -n 1)

#extracting
echo "[run_extract_resume.sh] extracting ..."
for d in $dir/state_*; do
    ./baut.py extract -d $d -n name suite $measures
done

#resuming
echo "[run_extract_resume.sh] resuming ..."
./util/numeric_resume.sh $dir $measures

echo "[run_extract_resume.sh] gluing all together ..."
./util/glue_all.sh $dir > $dir/run_stats.csv
