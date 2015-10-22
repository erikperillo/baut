#!/bin/bash

file_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

dir=$1

for d in $dir/*; do
	if [[ ! -z $(basename $d | grep "\.\|suite") ]]; then 
		continue
	else
		args=$args" "$d
	fi
done

$file_dir/glue.sh $args
