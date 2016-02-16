#!/bin/bash

file=$1

[[ -z $2 ]] && col_index=-1 || col_index=$2

if [[ $col_index -lt 0 ]]; then
	tail -n2 $file | head -n1 | rev | cut -f1 -d, | rev
else
	tail -n1 $file | head -n1 | cut -f$col_index -d, 
fi
