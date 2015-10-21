#!/bin/bash
#to be used in state_* kind of dir.
#ignores files containing "."

header=$(mktemp)
args=""

for f in $@; do
    if [[ ! -z $(basename $f | grep "\.") ]]; then
        continue
    else
        args=$args" "$f
    fi
done

for arg in $args; do
    printf $(basename $arg),
done > $header

cat $header | head -c -1
echo
paste -d, $args
