#!/bin/bash
#to be used in state_* kind of dir.
#ignores files containing "."

args=$@
header=$(mktemp)

for arg in $args; do
    printf $(basename $arg),
done > $header

cat $header | head -c -1
echo
paste -d, $args
