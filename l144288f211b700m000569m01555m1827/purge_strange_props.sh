#! /bin/bash

# Purge strange propagator files

sc=$1
ts=$2

if [ -z ${ts} ]
then
    echo "Usage $0 <seriescfg> <tsrc>"
    exit 1
fi

# Change seriescfg, tsrc format
seriescfg=`echo $sc | awk -F. '{printf("%s%06d",$1,$2)}'`
tsrc=`echo $ts | awk -F. '{printf("%s%03d",$1,$2)}'`

# Purge the heavy propagator files
dir=/home/detar/flare/allHISQ/scratch/prop/${seriescfg}/${ts}
echo "Removing strange propagator files for ${sc} ${tc}"
rm ${dir}/vol*/prop_F+qstrange* &

