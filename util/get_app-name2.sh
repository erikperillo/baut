#!/bin/bash

file=$1
suite=$2

([[ -z $file ]] || [[ -z $suite ]]) && { echo "error: invalid arguments"; exit 1; }

tmp_file=$(mktemp)
cat $file | sed "s/ /\n/g" > $tmp_file

case $suite in
	"npb"|"NPB")
		cat $tmp_file | grep "/local/erik/NPB" | cut -f1 -d, | rev | cut -f1 -d/ | rev ;;
	"splash2x"|"parsec")
  		cat $tmp_file | grep splash2x | cut -f2 -d. ;;
	"easy")
		cat $tmp_file | grep "/local/erik/tests/easy/bin/easy_" | cut -f1 -d, | rev \
					  | cut -f1 -d/ | cut -f1 -d_ | rev ;;
	*)
		echo "undefined"
esac
