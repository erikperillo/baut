#!/bin/bash

dir=$1

./baut.py extract -w $dir -exts exts/timer*

./baut.py stats -w $dir -m all

#./baut.py plot -w $dir -x interleave -y elapsed_s -yerr cin -show
