#!/usr/bin/env bash
# This script can be used, to collect test data of a RemoteHost.
#
# It is used like this:
# ./collect_test_output <remotehost_address> <hostname>

for folder in 'cpuinfo' 'fdisk' 'hostname' 'ifconfig' 'lsblk' 'lsblkl' 'meminfo' 'os-release' 'route'
do
    cmd=$(<$folder/.command)
    ssh $1 "$cmd" > $folder/$2
done
