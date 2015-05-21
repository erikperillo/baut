#!/bin/bash

cat | grep "timer_real:" | cut -f2 -d" "
