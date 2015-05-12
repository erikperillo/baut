#!/bin/bash

plotfile_template="/home/erik/docs/ic/benchmarks/plotfile.gplt.template"

dir=$1
size=$2

if [[ -z $dir ]]; then
	exit
fi
if [[ -z $size ]]; then
	size="1024,768"
fi

for bm in $dir/results/*; do
	bm_name=$(basename $bm)
	#echo "bm_name = $bm_name"
	#echo "output file:"
	sed "s-IN_FILE-$bm/time_results_no_header.csv-g; s/TITLE/$bm_name/g; s/SIZE/$size/g; s-OUT_IMG-$bm/chart.png-g" $plotfile_template > $bm/plotfile.gplt
	#sleep 5
	gnuplot $bm/plotfile.gplt
done
