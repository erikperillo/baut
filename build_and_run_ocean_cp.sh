#!/bin/bash

type=$1

cd /local/erik/parsec_custom/parsec-3.0/
(./build_ocean_cp.sh $type && parsecmgmt -a run -c gcc -p splash2x.ocean_cp -n 64 -i native)
