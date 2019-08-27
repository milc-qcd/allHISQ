#! /bin/bash

# Usage ./make_ssd_dirs.sh <LATS> <NCASES>

LATS=$1
NCASES=$2

if [ -z "${NCASES}" ]
then
  NCASES=1
fi

cfgs_milc=( `echo ${LATS} | sed 's|/| |g'` )
for((i=0; i<${NCASES}; i++)); do
  cfg_fnal=`echo ${cfgs_milc[$i]} | awk -F. '{if(length($1)==0)$1="a";printf("%s%06d",$1,$2)}'`

  path=/tmp/prop/${cfg_fnal}
  if [ ! -d ${path} ]
  then
    mkdir -p ${path}
  fi

  path=/tmp/rand/${cfg_fnal}
  if [ ! -d ${path} ]
  then
    mkdir -p ${path}
  fi

done
