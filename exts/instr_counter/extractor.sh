#!/bin/bash

cat | grep "instructions" | tr -s " " | rev | cut -f8 -d" " | rev | sed "s/,//g"
