#!/bin/bash
#gets time footprint 

file_dir=$( cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd )
name_last=$(cat $file_dir/last | rev | cut -f1 -d_ --complement | rev)
num=0
fp=$(date +"%D" | sed "s-/-_-g")

while [[ $fp == $name_last ]] && [[ $num -le $(cat $file_dir/last | rev | cut -f1 -d_ | rev) ]]; do
	num=$((num + 1))
done

echo -e $fp"_$num" | tee $file_dir/last 
