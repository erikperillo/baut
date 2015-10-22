#!/bin/bash
#to be run after $baut extract.

#getting this file directory
file_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

#getting baut dir and measures to take
baut_dir=$1
shift;
measures=$@

for d in $baut_dir/state_*; do
    echo "[resume.sh] in dir $d ..."
    (cd $d/results && $file_dir/glue.sh $measures > glued.csv)
    $file_dir/stat.py $d/results/glued.csv -a -H -m mean ci > $d/results/glued_stats.csv
done    
