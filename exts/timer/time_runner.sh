#!/bin/bash

args="$1"
while shift; do
	args+=" $1"
done

{ time $args > /dev/null; } 2>&1
