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
	#gluing numerical measures in one single file
    (cd $d/results && $file_dir/glue.sh $measures > glued.csv)
	#taking statistical measures of created file
    $file_dir/stat.py $d/results/glued.csv -a -H -m mean ci > $d/results/glued_stats.csv
done    

#gluing everything altogheter
$file_dir/glue_all.sh $baut_dir > $baut_dir/run_stats.csv
