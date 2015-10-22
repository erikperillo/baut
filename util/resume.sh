#!/bin/bash
#to be run after $baut extract.

file_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

baut_dir=$1
shift;
measures=$@

for d in $baut_dir/state_*; do
    echo "[resume.sh] in dir $d ..."
    $file_dir/glue_dir.sh $d/results $measures > $d/results/glued.csv
    $file_dir/stat.py "$d"/results/glued.csv -a -H -m mean ci > $d/results/glued_stats.csv
done    
