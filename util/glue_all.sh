#!/bin/bash
#glues everything in a run dir.

dir=$1
header_got=false

for d in $dir/state_*; do
	#echo "[glue_all.sh] in dir $d ..."

	#creating col with suite
	suite_with_header=$(mktemp)
	echo "suite,name,autonuma,interleave" > $suite_with_header
	suite_and_name=$(cat $d/results/suite),$(cat $d/results/name),$(cat $d/results/auto_numa),$(cat $d/results/interleave)
	echo $suite_and_name >> $suite_with_header

	if ! $header_got; then
		paste -d, $suite_with_header $d/results/glued_stats.csv | head -n 1
		header_got=true
	fi

	paste -d, $suite_with_header $d/results/glued_stats.csv | tail -n 1
done
