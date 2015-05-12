#!/bin/bash

numa_bal_ground="/proc/sys/kernel/numa_balancing"

nb=$numa_bal_ground
ss=$numa_bal_ground"_scan_size_mb"
sd=$numa_bal_ground"_scan_delay_ms"
spmin=$numa_bal_ground"_scan_period_min_ms"
spmax=$numa_bal_ground"_scan_period_max_ms"
md=$numa_bal_ground"_migrate_deferred"
sc=$numa_bal_ground"_settle_count"

#gatzalt
#printf "nb"$(cat $nb)"_md"$(cat $md)"_sc"$(cat $sc)"_ss"$(cat $ss)"_sd"$(cat $sd)"_spmin"$(cat $spmin)"_spmax"$(cat $spmax)
#pc
printf "nb"$(cat $nb)"_ss"$(cat $ss)"_sd"$(cat $sd)"_spmin"$(cat $spmin)"_spmax"$(cat $spmax)
