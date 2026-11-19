#! /bin/bash

# Usage ./make_ssd_dirs.sh

dir=/home/detar/flare/allHISQ/scratch

for d in DW_JOB_STRIPED/prop/*
do
    c=`basename $d`
    cmd="mkdir -p ${dir}/prop/${c}"
    echo ${cmd}
    ${cmd}
done

for d in DW_JOB_STRIPED/prop/*/*
do
    c=`echo $d | sed 's|DW_JOB_STRIPED/prop/||'`
    cmd="mkdir -p ${dir}/prop/${c}"
    echo ${cmd}
    ${cmd}
done

for d in DW_JOB_STRIPED/rand/*
do
    c=`basename $d`
    cmd="mkdir -p ${dir}/rand/${c}"
    echo ${cmd}
    ${cmd}
done

for d in DW_JOB_STRIPED/rand/*/*
do
    c=`echo $d | sed 's|DW_JOB_STRIPED/rand/||'`
    cmd="mkdir -p ${dir}/rand/${c}"
    echo ${cmd}
    ${cmd}
done

cmd="mkdir -p ${dir}/lat/v5"
echo ${cmd}
${cmd}

cmd="mkdir -p ${dir}/lat/ape"
echo ${cmd}
${cmd}


