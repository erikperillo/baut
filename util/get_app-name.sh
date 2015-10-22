#!/bin/bash
#determines app's name

#getting this file directory
file_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

#input
file=$1

#checking args
[[ -z $file ]] && { echo "error: invalid arguments"; exit 1; }

suite=$($file_dir/det_suite.sh $file)

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
