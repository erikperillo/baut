#!/bin/bash

file=$1

if [[ -z $(echo $(tail -n2 $file | head -n1) | grep "interleave") ]]; then
	echo 0
else
	echo 1
fi
