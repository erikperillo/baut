#!/bin/bash

file=$1

[[ -z $file ]] && { echo "error: must pass a file as argument"; exit 1; }

declare -a suites=("/local/erik/parsec-3.0/bin/parsecmgmt" "splash2x" "/local/erik/NPB2.3-omp-C/bin/" "NPB" "/local/erik/tests/easy/bin/" "easy")

for ((i=0; i<6; i+=2)); do
    pattern=${suites[$i]}
    if [[ ! -z $(grep "$pattern" $file) ]]; then
        echo ${suites[$((i + 1))]}
        exit
    fi
done

echo "undefined"
